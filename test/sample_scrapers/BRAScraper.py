import requests
from statscraper import Dataset

class BRA():
    """Scraper for Brottsförebyggande rådet."""
    url = 'http://statistik.bra.se'

    def describe(self):
        """Display metadata for a dataset."""
        raise NotImplementedError

    def get(self, fragment):
        raise NotImplementedError

    def fetch(self, params):
        """Fetch a dataset."""
        raise NotImplementedError

    def __repr__(self):
        return '<BRA instance: %s>' % self.url
