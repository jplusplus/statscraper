from unittest import TestCase

from statscraper.scrapers.SMHIScraper import SMHIScraper, Collection


class TestSMHI(TestCase):

    def test_smhi_scraper(self):
        """  """
        scraper = SMHIScraper()
        self.assertTrue(len(scraper.items))

    def test_fetch_dataset(self):
        """  """
        scraper = SMHIScraper()
        scraper.select("Radar")

        self.assertTrue(isinstance(scraper.current_item, Collection))
