#encoding:utf-8
from unittest import TestCase

from statscraper import (BaseScraper, Dataset, Dimension, AllowedValue,
    ROOT)


class Scraper(BaseScraper):

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")
        yield Dataset("Dataset_2")
        yield Dataset("Dataset_3")

    def _fetch_dimensions(self, dataset):
        yield Dimension(u"date")
        yield Dimension(u"municipality",
            allowed_values=["Robertsfors",u"Umeå"])

    def _fetch_data(self, dataset, query=None):
        yield {
            "date": "2017-08-10",
            "municipality": "Robertsfors",
            "value": 127
        }


class TestBaseScraper(TestCase):

    def test_init(self):
        """ Extending the basescraper """
        scraper = Scraper()
        self.assertTrue(scraper.current_item.id == ROOT)

    def test_inspect_item(self):
        """ Fecthing items from an itemlist """
        scraper = Scraper()
        self.assertTrue(scraper.items[0] == scraper.items.get("Dataset_1"))

    def test_select_item(self):
        scraper = Scraper()
        scraper.select("Dataset_1")
        self.assertTrue(isinstance(scraper.current_item, Dataset))

    def test_select_missing_item(self):
        # Should throw something like a KeyError?
        scraper = Scraper()
        scraper.select("non_existing_item")

    def test_fetch_dataset(self):
        scraper = Scraper()
        dataset = scraper.items[0]
        self.assertTrue(dataset.data[0]["municipality"] == "Robertsfors")

    def test_select_dimension(self):
        # I want to be able to select a dimension from a dataset
        scraper = Scraper()
        scraper.select("Dataset_1")
        dataset = scraper.current_item
        dim = dataset.dimension("date")
        self.assertTrue(isinstance(dim, Dimension))

        # Or is "select" a better method name?
        dim = dataset.get("date")
        self.assertTrue(isinstance(dim, Dimension))

    def test_select_allowed_value(self):
        scraper = Scraper()
        scraper.select("Dataset_1")
        dataset = scraper.current_item
        dim = dataset.dimension("municipality")
        municipality = dim.get("Robertsfors")

        self.assertTrue(isinstance(municipality, AllowedValue))
        self.addertEqual(municipality.id, "Robertsfors")
