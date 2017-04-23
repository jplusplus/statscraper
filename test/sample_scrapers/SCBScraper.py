import requests
import json
from statscraper import Dataset

class SCB():
    url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd'
    query = {'query': [], 'response': {}}

    def describe(self):
        """Display metadata for a dataset."""
        r = requests.get(self.url)
        self.content = r.json()
        return self.content

    def get(self, fragment):
        fragment = fragment.strip()
        if self.url.endswith('/'):
            if fragment.startswith('/'):
                fragment = fragment[1:]
        else:
            if not fragment.startswith('/'):
                fragment = '/%s' % fragment
        self.url += fragment
        return self

    def fetch(self, params):
        """Fetch a dataset."""
        _filter = {'code': params['code'], 'selection': {'filter': params['kind'], 'values': params['values']}}
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
