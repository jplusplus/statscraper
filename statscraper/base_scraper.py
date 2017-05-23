import csv
import requests


class BaseScraper():
    """Base class from which all scrapers inherit."""
    def select(self, label):
        """Select a dataset."""
        filterfunc = lambda x: x.label == label
        self.selection = next(filter(filterfunc, self._datasets))
        return self

    def list(self):
        """List all available datasets."""
        return [x.label for x in self._datasets]

    def fetch(self, params):
        """Make the actual request and fetch the data."""
        url = self._urls[self.selection.label]
        r = requests.get(url.format(**params))
        if 'filetype' in params:
            if params['filetype'] is 'csv':
                data = csv.DictReader(r.iter_lines(decode_unicode=True), delimiter=';')
            if params['filetype'] is 'json':
                data = r.json()
        data = r.text
        return self.selection.load(data)
