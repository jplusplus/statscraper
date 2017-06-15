# encoding: utf-8
import requests
import StringIO
import csvkit as csv
from datetime import datetime
from bs4 import BeautifulSoup

from statscraper import BaseScraper, Collection, Dataset

VERSION = "1.0"
# LEVELS = ["api","parameter"]
PERIODS = [
    "corrected-archive",
    "latest-hour",
    "latest-day",
    "latest-months",
]


class SMHIScraper(BaseScraper):
    base_url = "http://opendata.smhi.se/apidocs/"

    def _fetch_itemslist(self, current_item):
        """ Get a all available apis
        """
        if current_item.is_root:
            html = requests.get(self.base_url).text
            soup = BeautifulSoup(html, 'html.parser')
            for item_html in soup.select(".row .col-md-6"):
                try:
                    label = item_html.select_one("h2").text
                except Exception:
                    continue
                yield API(label, html_blob=item_html)
        else:
            # parameter = current_item.parent
            # data = requests.get(parameter.url)
            for resource in current_item.blob["resource"]:
                label = u"{}, {}".format(resource["title"], resource["summary"])
                yield SMHIDataset(label, blob=resource)

    def _fetch_dimensions(self, parameter):
        yield(Dimension("timepoint"))
        yield(Dimension("station"))
        yield(Dimension("period", allowed_values=PERIODS))

    def _fetch_data(self, dataset, query={}):
        """ Should yield dataset rows
        """
        data = []
        parameter = self.current_item
        # Step 1: Prepare query
        if "station" not in query:
            query["station"] = []

        all_stations = len(query["station"]) == 0

        if "period" not in query:
            # TODO: I'd prepare to do dataset.get("period").allowed_values here
            query["period"] = PERIODS

        elif not isinstance(query["period"], list):
            query["period"] = [query["period"]]

        for period in query["period"]:
            if period not in PERIODS:
                msg = u"{} is not an allowed period".format(period)
                raise Exception(msg)



        # Step 2: Get ids for all statiosn
        station_data = dataset.json_data
        stations = []

        for station in station_data["station"]:
            if station["name"] in query["station"] or all_stations:
                station = (station["key"], station["name"])
                stations.append(station)

        if len(stations) == 0:
            # TODO: More relevant exception class
            msg = u"No stations matched query: {}".format(query["station"])
            raise Exception(msg)

        # Step 3: Get data
        n_queries = len(stations) * len(query["period"])
        print "Fetching data with {} queries.".format(n_queries)
        for station_key, station_name in stations:
            for period in query["period"]:

                url = dataset.url\
                    .replace(".json", "/station/{}/period/{}/data.csv"\
                        .format(station_key, period))

                print "/GET {}".format(url)
                r = requests.get(url)

                if r.status_code == 200:
                    raw_data = DataCsv().from_string(r.content).to_dictlist()

                    # TODO: This is a very hard coded parse function
                    # Expects fixed start row and number of cols
                    for row in raw_data:
                        if "Datum" in row and "Tid (UTC)" in row:
                            timepoint_str = "{} {}".format(
                                row["Datum"], row["Tid (UTC)"])
                        elif u"Från Datum Tid (UTC)":
                            timepoint_str = row[u"Från Datum Tid (UTC)"]

                        timepoint = datetime.strptime(timepoint_str, "%Y-%m-%d %H:%M:%S")
                        # HACK!
                        # Should rather be something like parameter.col_name
                        value_col = parameter.id.split(",")[0]
                        data.append({
                            "timepoint": timepoint,
                            "quality": row["Kvalitet"],
                            "parameter": parameter.id,
                            "station": station_name,
                            "period": period,
                            "value": row[value_col],
                            })

                elif r.status_code == 404:
                    print("Warning no data at {}".format(url))
                else:
                    raise Exception("Connection error for {}".format(url))

        return data

class API(Collection):
    level = "api"

    def __init__(self, _id, html_blob=None):
        self.id = _id
        self.key = html_blob.select_one("a").get("href").replace("/index.html", "")
        self.url = "http://opendata-download-{}.smhi.se/api/version/{}.json"\
            .format(self.key, VERSION)

    @property
    def blob(self):
        return self._get_json_blob()

    def _get_json_blob(self):
        # Update blob
        error_msg = "Scraper does not support parsing of '{}' yet.".format(self.id)
        try:
            r = requests.get(self.url)
        except Exception:
            # Catch ie. "opendata-download-grid.smhi.se"
            raise NotImplementedError(error_msg)
        if r.status_code == 404:
            raise NotImplementedError(error_msg)

        return r.json()


class SMHIDataset(Dataset):
    @property
    def key(self):
        return self.blob["key"]

    @property
    def url(self):
        api = self.scraper.parent
        return "http://opendata-download-{}.smhi.se/api/version/{}/parameter/{}.json"\
            .format(api.key, VERSION, self.key)

    @property
    def json_data(self):
        if not hasattr(self, "_json_data"):
            print self.url
            self._json_data = requests.get(self.url).json()
        return self._json_data

class DataCsv(object):
    def __init__(self):
        self.headers = None
        self.data = None


    def from_file(self, file_path):
        with open(file_path) as f:
            self._parse(f)

        return self

    def from_string(self, csv_content):
        f = StringIO.StringIO(csv_content)
        self._parse(f)

        return self

    def to_dictlist(self):
        return [dict(zip(self.headers, row))
            for row in self.data]

    def _parse(self, f):
        rows = list(csv.reader(f, delimiter=';'))
        tables = []
        table = []
        for i, row in enumerate(rows):
            is_last = i == len(rows) - 1

            # Check if new table
            if is_empty(row):
                if len(table) > 0:
                    tables.append(table)
                table = []
                continue

            is_header = len(table) == 0
            if is_header:
                n_cols = table_width(row)

            table.append(row[:n_cols])

            if is_last:
                tables.append(table)

        data_table = tables[-1]
        self.headers = data_table[0]
        try:
            self.data = data_table[1:]
        except IndexError:
            self.data = []

def is_empty(row):
    """ Check if a csv row (represented as a list
        of values) is empty.

        [] => True
        ["","","foo"] => True
        ["foo","bar"] => False
    """
    if len(row) == 0:
        return True
    if row[0] == "":
        return True
    return False

def table_width(row):
    """ Get number of cols in row
        ["col1", "col2","","","other_col"] => 2
    """

    for i, val in enumerate(row):
        if val == "":
            break
    return i

