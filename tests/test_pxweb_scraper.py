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
        scraper.move_to("Befolkning")\
               .move_to(u"Födda")\
               .move_to(u"Befolkningsförändringar efter område 1980 - 2016")
        data = scraper.fetch()
        self.assertTrue(len(data))

