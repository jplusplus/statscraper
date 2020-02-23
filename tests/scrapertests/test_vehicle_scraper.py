# encoding: utf-8

from unittest import TestCase
from statscraper.scrapers import Vehicles


class TestVehicles(TestCase):

    def setUp(self):
        self.scraper = Vehicles()

    def test_has_items(self):
        self.assertTrue(len(self.scraper.items))

    def test_has_datasets(self):
        datasets = self.scraper.items
        self.assertTrue(len(datasets))

    def test_can_fetch(self):
        dataset = self.scraper.items[0]
        data = dataset.fetch(query={'years': [2017], 'months':[0,1]})
        self.assertTrue(len(data))