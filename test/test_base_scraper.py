from unittest import TestCase

from statscraper import BaseScraper, Dataset, Dimension


class Scraper(BaseScraper):

    def _fetch_itemslist(self, item):
        yield Dataset("Dataset_1")

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

    def test_base_scraper(self):
        """ Extending the basescraper """
        scraper = Scraper()

        self.assertTrue(len(scraper.items))
        self.assertTrue(scraper.items[0] == scraper.items.get("Dataset_1"))

        dataset = scraper.items[0]

        self.assertTrue(len(dataset.dimensions))
        self.assertTrue(dataset.data[0]["municipality"] == "Robertsfors")
