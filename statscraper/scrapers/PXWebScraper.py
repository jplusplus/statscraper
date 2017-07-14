# encoding: utf-8
""" A wrapper around the PX-Web API. As implementations
    and versions vary, this is best used as a base class,
    for more specific scrapers to extend.

    If used directly, an API endpoint must be set:
        scraper = PXWeb(base_url="http://api.example.com/")
        # ...or:
        scraper = PXWeb()
        scraper.base_url = "http://api.example.com/"
"""

import requests
from statscraper import (BaseScraper, Collection, Result,
                         Dataset, Dimension, InvalidData)
from statscraper.compat import JSONDecodeError


class PXWeb(BaseScraper):

    base_url = None  # API endpoint

    @BaseScraper.on("init")
    def _get_args(self, *args, **kwargs):
        """ Store `base_url`, if given on init. This is convenient when
            the PXWeb scraper is used directly by an end user.
        """
        if "base_url" in kwargs and kwargs["base_url"]:
            self.base_url = kwargs["base_url"]

    def _api_path(self, item):
        """Get the API path for the current cursor position."""
        if self.base_url is None:
            raise NotImplementedError("base_url not set")
        path = "/".join([x.blob["id"] for x in item.path])
        return "/".join([self.base_url, path])

    def _fetch_itemslist(self, item):
        data = requests.get(self._api_path(item)).json()

        for d in data:
            if d["type"] == "l":
                yield Collection(d["id"], label=d["text"], blob=d)
            else:
                yield Dataset(d["id"], label=d["text"], blob=d)

    def _fetch_dimensions(self, dataset):
        data = requests.get(self._api_path(dataset)).json()
        try:
            for d in data["variables"]:
                yield Dimension(d["code"],
                                label=d["text"],
                                allowed_values=d["values"])

        except KeyError:
            yield None

    def _fetch_data(self, dataset, query, filtertype="item"):
        if query is None:
            query = {}
        body = {
            'query': [{
                'code': key,
                'selection': {
                    'filter': filtertype,
                    # value can be a list or a value
                    'values': value if isinstance(value, list) else [value]
                }
            } for key, value in query.iteritems()],
            'response': {
                'format': "json"
            }
        }
        try:
            raw = requests.post(self._api_path(dataset), json=body)
            data = raw.json()
        except JSONDecodeError:
            raise InvalidData("""No valid response from PX Web.
Check your query for spelling errors, or try reducing the size.
This error is frequently due to a too large result being requested.""")

        # All available dimensions are not always returned.
        # What is returned depends on the query
        raw_return_dimension = data["columns"]
        # Filter out dimensions only
        raw_return_dimension = [x for x in raw_return_dimension if x["type"] != "c"]

        for row in data[u"data"]:
            for value in row[u"values"]:
                dimensions = {}
                # 'key' contains one value for each dimension,
                # always preserving order.
                for d, v in zip(raw_return_dimension, row[u"key"]):
                    dimensions[d["code"]] = v

                yield Result(value, dimensions=dimensions)
