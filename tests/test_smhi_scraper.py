# encoding: utf-8
from unittest import TestCase

from statscraper.scrapers.SMHIScraper import SMHIScraper, Collection


class TestSMHI(TestCase):

    def test_smhi_scraper(self):
        """Setting up scraper."""
        scraper = SMHIScraper()
        self.assertTrue(len(scraper.items))

    def test_fetch_dataset(self):
        u"""Moving to an “API”."""
        scraper = SMHIScraper()
        scraper.move_to("Radar")

        self.assertTrue(isinstance(scraper.current_item, Collection))
