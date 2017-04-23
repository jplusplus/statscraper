import unittest
import json
from .sample_scrapers.SCBScraper import SCB

class TestSCB(unittest.TestCase):
    """Tests SCB scraper."""
    def setUp(self):
        self.scb = SCB()
        self.scb.get('BE/BE0101/BE0101H/FoddaK')

    def test_fetch(self):
        dataset = self.scb.fetch({
            'code':'Tid', 
            'kind':'item', 
            'values':['2014'], 
            'format':'json'
        })
        self.assertIn('år', dataset.dimensions)
        self.assertIn('Levande födda', dataset.dimensions)
        self.assertEqual(dataset.data[1][2], '29496')
