import requests
import csv
from bs4 import BeautifulSoup
from statscraper import Dataset

class SOS():
    """Scraper for Socialstyrelsen."""
    url = 'http://www.socialstyrelsen.se/statistik/statistikdatabas'

    def describe(self):
        """Display metadata for a dataset."""
        raise NotImplementedError

    def select(self, identifier, by_label=True):
        if not by_label:
            self.url = '{}/{}'.format(self.url, identifier)
        else:
            label = next(filter(lambda x: x['text'] == identifier, self.topics)).get('id')
            self.url = '{}/{}'.format(self.url, label)
        return self

    def unselect(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    @property
    def topics(self):
        if hasattr(self, '_topics'):
            return self._topics
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, 'html.parser')
        items = soup.select('#socextPageBody ul > li > a')
        return [{'text': x.text, 'id': x['href']} for x in items]

    def fetch(self, params):
        """Fetch a dataset."""

        # Temporary hardcoded data for testing
        data = {
            'MATT':'HL',
            'hOmrTyp':'HL',
            'i_7_2':'on',
            'OMR':1,
            'uAGI':'05',
            'oAGI':18,
            'KON':1,
            'AR':2011,
            'TYP':'TABELL',
            'haDIA':1,
            'hvDIA':';7;',
            'haOMR':1,
            'hvOMR':';1;',
            'vKON':';1;',
            'vAR':';2011;',
            'hvDIA2':';i_7_2;'
        }
        r = requests.post('http://sdb.socialstyrelsen.se/if_hji/resultat.aspx', data=data)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.select_one('#ph1_GridView1')
        dims = [x.text for x in table.select('th')]
        values = []
        for row in table.select('tr')[1:]:
            outrow = []
            for value in row.select('td'):
                outrow.append(value.text)
            values.append(outrow)
        dataset = Dataset(label='Temp', dimensions=dims)
        dataset.load(values)
        return dataset


    def __repr__(self):
        return '<SOS instance: %s>' % self.url
