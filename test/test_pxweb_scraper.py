from unittest import TestCase

from statscraper.scrapers.PXWebScraper import PXWeb


class TestPXWeb(TestCase):

    def test_pxweb_scraper(self):
        """ Setup an run a PXWeb scraper, make sure we get
            some collections from a reliabel source.
        """
        scraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")
        self.assertTrue(len(scraper.items))
