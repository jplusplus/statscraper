# encoding: utf-8
import requests
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
                yield Dataset(label, blob=resource)

    def _fetch_dimensions(self, dataset):
        self.url = "http://opendata-download-{}.smhi.se/api/version/{}/parameter/{}.json"\
            .format(dataset.key, VERSION, )
        parameter = self.parent

        data = requests.get(parameter.url)
        for resource in self.current_item.blob["resource"]:
            key = resource["key"]
            #label = u"{}, {}".format(resource["title"], resource["summary"])
            yield SMHIDataset(key, blob=resource)

    def _fetch_dimensions(self, parameter):
        yield(Dimension("timepoint"))
        yield(Dimension("station"))
        yield(Dimension("period", allowed_values=PERIODS))

    def _fetch_data(self, dataset, query=None):
        """ Should yield dataset rows
        """

        data = dataset.json_data
        raise NotImplementedError("work in progress")


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
    def url(self):
        # Här vill jag hämta in
        api = self.scraper.current_item
        return "http://opendata-download-{}.smhi.se/api/version/{}/parameter/{}.json"\
            .format(api.key, VERSION, self.id)

    @property
    def json_data(self):
        if not hasattr(self, "_json_data"):
            self._json_data = requests.get(self.url).json()
        return self._json_data

