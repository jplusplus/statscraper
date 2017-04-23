import requests
from statscraper import Dataset

class BRA():
    """Scraper for Brottsförebyggande rådet."""
    url = 'http://statistik.bra.se'

    def describe(self):
        """Display metadata for a dataset."""
        raise NotImplementedError

    def select(self, fragment):
        raise NotImplementedError

    def unselect(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    @property
    def topics(self):
        raise NotImplementedError

    def fetch(self, params):
        """Fetch a dataset."""
        raise NotImplementedError

    def __repr__(self):
        return '<BRA instance: %s>' % self.url
