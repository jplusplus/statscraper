# encoding:utf-8
from unittest import TestCase

from statscraper import (BaseScraper, Dataset, Dimension, AllowedValue,
                         ROOT, NoSuchItem)


class Scraper(BaseScraper):

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")
        yield Dataset("Dataset_2")
        yield Dataset("Dataset_3")

    def _fetch_dimensions(self, dataset):
        yield Dimension(u"date")
        yield Dimension(u"municipality",
                        allowed_values=["Robertsfors", u"Umeå"])

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
        """ Moving the cursor up and down the tree,
            selecting by id and reference """
        scraper = Scraper()
        scraper.select("Dataset_1")
        self.assertTrue(isinstance(scraper.current_item, Dataset))

        scraper.up()
        scraper.select(scraper.items[0])
        self.assertTrue(isinstance(scraper.current_item, Dataset))

    def test_stop_at_root(self):
        """ Trying to move up from the root should do nothing """
        scraper = Scraper()
        scraper.up().up().up().up()
        self.assertTrue(scraper.current_item.id == ROOT)

    def test_select_missing_item(self):
        """ Select an Item by ID that doesn't exist """
        scraper = Scraper()
        with self.assertRaises(NoSuchItem):
            scraper.select("non_existing_item")

    def test_item_knows_parent(self):
        """ Make sure an item knows who its parent is """
        scraper = Scraper()
        dataset = scraper.items.get("Dataset_1")
        scraper.select(dataset)
        self.assertTrue(scraper.parent.id == dataset.parent.id)

    def test_fetch_dataset(self):
        """ Auery a dataset for some data """
        scraper = Scraper()
        dataset = scraper.items[0]
        self.assertTrue(dataset.data[0]["municipality"] == "Robertsfors")

    def test_get_dimension(self):
        """ Get dimensions for a dataset """
        scraper = Scraper()
        dataset = scraper.items[0]
        self.assertTrue(len(dataset.dimensions))
        self.assertTrue(isinstance(dataset.dimensions[0], Dimension))

    def test_select_allowed_value(self):
        scraper = Scraper()
        scraper.select("Dataset_1")
        dataset = scraper.current_item
        dim = dataset.dimension("municipality")
        municipality = dim.get("Robertsfors")

        self.assertTrue(isinstance(municipality, AllowedValue))
        self.addertEqual(municipality.id, "Robertsfors")
