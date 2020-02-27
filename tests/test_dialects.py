"""Tests related to the concept of certain datatypes having values with dialects."""
from unittest import TestCase
from statscraper import (BaseScraper, Dataset, Result, Dimension, DimensionValue)


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
        yield Result(17, {
            "municipality": "Region Gotland",
        })


class TestDialects(TestCase):
    """Test translated values."""

    def test_translations(self):
        """Test standalone translation."""
        municipalities = Dimension("municipality",
                                   datatype="region", domain="sweden/municipalities")
        municipality = DimensionValue("Stockholms kommun", municipalities)
        assert municipality.translate("numerical") == "180"

    def test_dialects(self):
        """Test translation inside a scraper."""
        scraper = Scraper()
        data1 = scraper.items[0].data
        self.assertEqual(str(data1[0]["municipality"]), "Robertsfors kommun")

        data2 = data1.translate("scb")
        self.assertEqual(str(data2[0]["municipality"]), "2409 Robertsfors kommun")
