# encoding: utf-8
from unittest import TestCase

from statscraper.scrapers.VantetiderScraper import VantetiderScraper


class TestVantetider(TestCase):

    def setUp(self):
        self.scraper = VantetiderScraper()

    def test_smhi_scraper(self):
        """Setting up scraper."""
        self.assertTrue(len(self.scraper.items))


    def test_fetch_dataset(self):
        u"""Moving to an “API”."""
        dataset = self.scraper.get("PrimarvardBesok")

        #self.assertTrue(isinstance(dataset, Dataset))
        self.assertEqual(len(self.scraper.items), 9)


    def test_fetch_dimensions(self):
        u"""Moving to an “API”."""
        for dataset in self.scraper.items:
            self.assertGreater(len(dataset.dimensions),0)

    def test_basic_query(self):
        dataset = self.scraper.get("PrimarvardTelefon")
        res = dataset.fetch({"region": ["Blekinge"]})
        df = res.pandas
        self.assertGreater(df.shape[0],0)

    def test_multi_period_query(self):
        dataset = self.scraper.get("PrimarvardBesok")
        res = dataset.fetch({
            "region": ["Stockholm"],
            "year": ["2017", "2016"]
            })
        df = res.pandas
        self.assertGreater(df.shape[0],0)
