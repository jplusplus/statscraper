from unittest import TestCase

from statscraper.scrapers.PXWebScraper import PXWeb


class TestPXWeb(TestCase):

    def test_pxweb_scraper(self):
        """ Extending the PXWebScraper """
        pxscraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")
        self.assertTrue(len(pxscraper.items))
