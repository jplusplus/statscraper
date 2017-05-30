# encoding: utf-8
""" A wrapper around the Statistikcentralen/Tilastokeskus API,
    demonstrating how to extend a scraper in the scraper park.

    The user can select 'fi' or 'sv' as their prefered language like this:

     scraper = Statistikcentralen("fi")
     # ...or:
     scraper = Statistikcentralen()
     scraper.lang = "fi"
"""
from PXWebScraper import PXWeb


class Statistikcentralen(PXWeb):

    lang = "sv"
    _available_languages = ["sv", "fi"]

    @property
    def base_url(self):
        return 'http://pxnet2.stat.fi/pxweb/api/v1/%s/StatFin/' % self.lang

    @PXWeb.on("init")
    def _get_lang(self, *args, **kwargs):
        """ Let users select language
        """
        if "lang" in kwargs:
            if kwargs["lang"] in self._available_languages:
                self.lang = kwargs["lang"]
