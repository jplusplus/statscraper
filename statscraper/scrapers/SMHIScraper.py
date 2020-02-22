# encoding: utf-8
try:
    import StringIO
except ImportError:
    import io as StringIO

import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup

from statscraper import BaseScraper, Collection, Dimension, Dataset, Result, ResultSet, NoSuchItem, DimensionValue

VERSION = "1.0"
# LEVELS = ["api","parameter"]
PERIODS = [
    "corrected-archive",
    "latest-hour",
    "latest-day",
    "latest-months",
]


class SMHI(BaseScraper):
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
                yield API(label, blob=item_html)
        else:
            # parameter = current_item.parent
            # data = requests.get(parameter.url)
            for resource in current_item.json["resource"]:
                label = u"{}, {}".format(resource["title"], resource["summary"])
                yield SMHIDataset(label, blob=resource)

    def _fetch_dimensions(self, parameter):
        yield(StationDimension("station"))
        # Hack: This redundant of the station dimension, but
        # necessary to be able to include both station name
        # (=readabilty) and key in resultset.
        # It would be better if the ResultSet object could
        # handle both label and key print.
        yield(Dimension("station_key"))
        yield(Dimension("period", allowed_values=PERIODS))
        yield(Dimension("parameter"))

        example_data = parameter._get_example_csv()
        for dim in example_data.columns:
            yield(Dimension(dim))


    def _fetch_allowed_values(self, dimension):
        if dimension.id == "station":
            for station in dimension.dataset.json["station"]:
                yield Station(station["key"], dimension,
                    label=station["name"],blob=station)
        else:
            yield None

    def _fetch_data(self, dataset, query={}, include_inactive_stations=False):
        """ Should yield dataset rows
        """
        data = []
        parameter = dataset
        station_dim = dataset.dimensions["station"]
        all_stations = station_dim.allowed_values
        # Step 1: Prepare query
        if "station" not in query:
            if include_inactive_stations:
                # Get all stations
                query["station"] = list(all_stations)
            else:
                # Get only active stations
                query["station"] = list(station_dim.active_stations())
        else:
            if not isinstance(query["station"], list):
                query["station"] = [query["station"]]
            # Make sure that the queried stations actually exist
            query["station"] = [ all_stations.get_by_label(x) for x in query["station"]]

        if "period" not in query:
            # TODO: I'd prepare to do dataset.get("period").allowed_values here
            query["period"] = PERIODS

        elif not isinstance(query["period"], list):
            query["period"] = [query["period"]]

        for period in query["period"]:
            if period not in PERIODS:
                msg = u"{} is not an allowed period".format(period)
                raise Exception(msg)


        # Step 3: Get data
        n_queries = len(query["station"]) * len(query["period"])
        counter = 0
        print("Fetching data with {} queries.".format(n_queries))
        for station in query["station"]:
            for period in query["period"]:
                url = dataset.url\
                    .replace(".json", "/station/{}/period/{}/data.csv"\
                        .format(station.key, period))
                print("/GET {} ".format(url))
                r = requests.get(url)

                if r.status_code == 200:
                    raw_data = DataCsv().from_string(r.content).to_dictlist()

                    # TODO: This is a very hard coded parse function
                    # Expects fixed start row and number of cols
                    for row in raw_data:
                        #timepoint = datetime.strptime(timepoint_str, "%Y-%m-%d %H:%M:%S")
                        value_col = parameter.id.split(",")[0]
                        value = float(row[value_col])

                        row["parameter"] = parameter.id
                        row["station"] = station.label
                        row["station_key"] = station.key
                        row["period"] = period

                        row.pop(value_col,None)

                        datapoint = Result(value, row)

                        yield datapoint

                elif r.status_code == 404:
                    print("Warning no data at {}".format(url))
                else:
                    raise Exception("Connection error for {}".format(url))


class API(Collection):
    """
    """
    level = "api"

    @property
    def key(self):
        return self.blob.select_one("a").get("href").replace("/index.html", "")

    @property
    def url(self):
        return "http://opendata-download-{}.smhi.se/api/version/{}.json"\
                .format(self.key, VERSION)

    @property
    def json(self):
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


class StationDimension(Dimension):

    def active_stations(self):
        """ Get a list of all active stations
        """
        return (x for x in self.allowed_values if x.is_active)

class Station(DimensionValue):
    def __init__(self, value, dimension, label=None, blob=None):
        super(Station, self).__init__(value, dimension, label=label)

        self.key = value
        self.summary = blob["summary"]
        self.updated = datetime.fromtimestamp(blob["updated"]/1000)
        self.blob = blob

        # Was there an update in the last 100 days?
        self.is_active = (datetime.now() - self.updated).days < 100


    def __repr__(self):
        if self.is_active:
            status = "active"
        else:
            status = "inactive"
        return "<Station: {} ({})>"\
            .format(self.label.encode("utf-8"), status)

class SMHIDataset(Dataset):
    @property
    def key(self):
        return self.blob["key"]

    @property
    def url(self):
        api = self.parent
        return "http://opendata-download-{}.smhi.se/api/version/{}/parameter/{}.json"\
            .format(api.key, VERSION, self.key)

    @property
    def json(self):
        if not hasattr(self, "_json"):
            print(self.url)
            self._json = requests.get(self.url).json()
        return self._json


    def get_stations_list(self):
        """ Get a dict list of all stations with properties such as
            latitude and longitude
        """
        stations = self.dimensions["station"].allowed_values
        return self._format_station_list(stations)


    def get_active_stations_list(self):
        """ Get a dict list of all stations with properties such as
            latitude and longitude
        """
        stations = self.dimensions["station"].active_stations()
        return self._format_station_list(stations)

    def _get_example_csv(self):
        """For dimension parsing
        """
        station_key = self.json["station"][0]["key"]
        period = "corrected-archive"
        url = self.url\
                  .replace(".json", "/station/{}/period/{}/data.csv"\
                  .format(station_key, period))

        r = requests.get(url)
        if r.status_code == 200:
            return DataCsv().from_string(r.content)
        else:
            raise Exception("Error connecting to api")


    def _format_station_list(self, stations):
        data = []
        for station in stations:
            json_data = station.blob
            # Inlude all props but link
            json_data.pop('link', None)
            data.append(station.blob)

        return data


class DataCsv(object):
    columns = []
    data = []

    def from_file(self, file_path):
        with open(file_path) as f:
            self._parse(f)

        return self

    def from_string(self, csv_content):
        f = StringIO.StringIO(csv_content)
        self._parse(f)

        return self

    def to_dictlist(self):
        return [dict(zip(self.columns, row))
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
        self.columns = data_table[0]
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
