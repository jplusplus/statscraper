from unittest import TestCase

from statscraper.scrapers.PXWebScraper import PXWeb


class TestPXWeb(TestCase):

    def test_pxweb_scraper(self):
        """ Extending the basescraper """
        scraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")
        self.assertTrue(len(scraper.items))
