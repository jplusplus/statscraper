from unittest import TestCase

from statscraper import BaseScraper, Dataset, Dimension, ROOT


class Scraper(BaseScraper):

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")
        yield Dataset("Dataset_2")
        yield Dataset("Dataset_3")

    def _fetch_dimensions(self, dataset):
        yield Dimension(u"date")
        yield Dimension(u"municipality")

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

    def test_fetch_dataset(self):
        scraper = Scraper()
        dataset = scraper.items[0]
        self.assertTrue(dataset.data[0]["municipality"] == "Robertsfors")
