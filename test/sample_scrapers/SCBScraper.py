# encoding: utf-8
import requests
import json
from ...statscraper import Dataset


class SCB():
    base_url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd'
    url = base_url
    cached_url = None
    query = {'query': [], 'response': {}}

    def describe(self):
        """Display metadata for a dataset."""
        r = requests.get(self.url)
        self.content = r.json()
        return self.content

    def select(self, identifier, by_label=True):
        """Select a topic or dataset by label or unique identifier."""
        if not by_label:
            self.url = '{}/{}'.format(self.url, identifier)
        else:
            label = next(filter(lambda x: x['text'] == identifier, self.topics)).get('id')
            self.url = '{}/{}'.format(self.url, label)
        return self

    def unselect(self):
        """Unselect, or "rewind", a previous selection."""
        self.url = self.url.rsplit('/', 1)[0]

    def reset(self):
        """Go back to the root level."""
        self.url = self.base_url

    @property
    def topics(self):
        """List topics at the current level. Do some light-weight caching."""
        if self.cached_url == self.url:
            return self._topics
        self.cached_url = self.url
        r = requests.get(self.url)
        self._topics = r.json()
        return self._topics

    def fetch(self, params):
        """Fetch a dataset."""
        _filter = {
            'code': params['code'],
            'selection': {
                'filter': params['kind'],
                'values': params['values']
            }
        }
        self.query['query'] = [_filter]

        self.query['response'] = {'format': params['format']}
        self.r = requests.post(self.url, data=json.dumps(self.query))
        if params['format'] == 'json':
            return process_data(json.loads(self.r.content))
        return self.r.content

    def __repr__(self):
        return '<SCB instance: %s>' % self.url


def process_data(indata):
    dims = [x['text'] for x in indata['columns']]
    records = [x['key'] + x['values'] for x in indata['data']]
    data = Dataset(label='Temp', dimensions=dims)
    data.load(records)
    return data
