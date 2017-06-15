# encoding:utf-8
from unittest import TestCase

from statscraper import (BaseScraper, Dataset, Dimension, AllowedValue,
                         ROOT, NoSuchItem)


class Scraper(BaseScraper):
    """A scraper with hardcoded yields."""

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")
        yield Dataset("Dataset_2")
        yield Dataset("Dataset_3")

    def _fetch_dimensions(self, dataset):
        yield Dimension(u"date")
        yield Dimension(u"municipality",
                        allowed_values=["Robertsfors", u"Umeå"])

    def _fetch_data(self, dataset, query=None):
        if dataset.id == "Dataset_1":
            yield {
                "date": "2017-08-10",
                "municipality": "Robertsfors",
                "value": 127
            }
        elif dataset.id == "Dataset_2":
            yield {
                "date": "2017-02-06",
                "municipality": "Umeå",
                "value": 12
            }
            yield {
                "date": "2017-02-07",
                "municipality": "Robertsfors",
                "value": 130
            }


class TestBaseScraper(TestCase):
    """Testing base functionality."""

    def test_init(self):
        """Extending the basescraper."""
        scraper = Scraper()
        self.assertTrue(scraper.current_item.id == ROOT)

    def test_inspect_item(self):
        """Fetching items from an itemlist."""
        scraper = Scraper()
        self.assertTrue(scraper.items[0] == scraper.items["Dataset_1"])

    def test_move_to_item(self):
        """Moving the cursor up and down the tree."""
        scraper = Scraper()
        scraper.move_to("Dataset_1")
        self.assertTrue(isinstance(scraper.current_item, Dataset))
        self.assertTrue(scraper.current_item.id == "Dataset_1")

        scraper.move_up()
        scraper.move_to(1)
        self.assertTrue(isinstance(scraper.current_item, Dataset))
        self.assertTrue(scraper.current_item.id == "Dataset_2")

        scraper.move_up()
        scraper.move_to(scraper.items[2])
        self.assertTrue(isinstance(scraper.current_item, Dataset))
        self.assertTrue(scraper.current_item.id == "Dataset_3")

    def test_chained_move_to(self):
        """Use chaining to move."""
        scraper = Scraper()
        scraper.move_to("Dataset_1").move_up().move_to("Dataset_2")
        self.assertTrue(scraper.current_item.id == "Dataset_2")

    def test_stop_at_root(self):
        """Trying to move up from the root should do nothing."""
        scraper = Scraper()
        scraper.move_up().move_up().move_up().move_up()
        self.assertTrue(scraper.current_item.is_root)

    def test_select_missing_item(self):
        """Select an Item by ID that doesn't exist."""
        scraper = Scraper()
        with self.assertRaises(NoSuchItem):
            scraper.move_to("non_existing_item")

    def test_item_knows_parent(self):
        """Make sure an item knows who its parent is."""
        scraper = Scraper()
        dataset = scraper.items["Dataset_1"]
        scraper.move_to("Dataset_1")
        self.assertTrue(scraper.parent.id == dataset.parent.id)

    def test_fetch_dataset(self):
        """Query a dataset for some data."""
        scraper = Scraper()
        dataset = scraper.items[0]
        self.assertTrue(dataset.data[0]["municipality"] == "Robertsfors")

    def test_get_dimension(self):
        """ Get dimensions for a dataset """
        scraper = Scraper()
        dataset = scraper.items[0]
        self.assertTrue(len(dataset.dimensions))
        self.assertTrue(isinstance(dataset.dimensions[0], Dimension))

        dim = dataset.dimension("municipality")
        self.assertTrue(isinstance(dim, Dimension))

    def test_select_allowed_value(self):
        scraper = Scraper()
        dataset = scraper.items[0]

        dim = dataset.dimension("municipality")
        municipality = dim.get("Robertsfors")

        self.assertTrue(isinstance(municipality, AllowedValue))
        self.addertEqual(municipality.id, "Robertsfors")
