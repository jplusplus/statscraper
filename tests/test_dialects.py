# encoding: utf-8

from unittest import TestCase
from statscraper import (BaseScraper, Dataset, Result, Dimension)


class Scraper(BaseScraper):
    """A scraper with hardcoded yields."""

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")

    def _fetch_dimensions(self, dataset):
        yield Dimension(u"municipality", datatype="region")

    def _fetch_data(self, dataset, query=None):
        yield Result(127, {
            "municipality": "Robertsfors kommun",
        })


class TestDialects(TestCase):

    def test_dialects(self):
        """Covert a resultset to a different dialect."""
        scraper = Scraper()
        data1 = scraper.items[0].data
        self.assertEqual(str(data1[0]["municipality"]), "Robertsfors kommun")

        data2 = data1.translate("scb")
        self.assertEqual(str(data2[0]["municipality"]), "2409 Robertsfors kommun")

