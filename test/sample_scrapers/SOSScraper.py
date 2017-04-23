import requests
import json
from statscraper import Dataset

class SOS():
    """Scraper for Socialstyrelsen."""
    url = 'http://www.socialstyrelsen.se/statistik/statistikdatabas'

    def describe(self):
        """Display metadata for a dataset."""
        raise NotImplementedError

    def get(self, fragment):
        raise NotImplementedError

    def fetch(self, params):
        """Fetch a dataset."""
        raise NotImplementedError

    def __repr__(self):
        return '<SOS instance: %s>' % self.url
