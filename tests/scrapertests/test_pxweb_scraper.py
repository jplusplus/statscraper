# encoding: utf-8

from unittest import TestCase

from statscraper.scrapers import PXWeb


class TestPXWeb(TestCase):

    def test_init_scraper(self):
        """Extending the PXWebScraper."""
        pxscraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")
        self.assertTrue(len(pxscraper.items))

    def test_navigating_tree(self):
        """Navigate the tree.."""
        scraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")
        scraper.move_to("tym")\
               .move_to(u"tyonv")\
               .move_to(u"statfin_pxt_tym_tyonv_001.px")
        data = scraper.fetch()
        self.assertTrue(len(data))
