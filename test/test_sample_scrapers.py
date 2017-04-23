import unittest
import json
from .sample_scrapers.SCBScraper import SCB
from .sample_scrapers.SOSScraper import SOS
from .sample_scrapers.BRAScraper import BRA

class TestSCB(unittest.TestCase):
    """Tests SCB scraper."""
    def setUp(self):
        self.scb = SCB()

    def test_list_topics(self):
        self.assertIn('Nationalräkenskaper', [x['text'] for x in self.scb.topics])

    def test_list_subtopics(self):
        self.scb.select('Levnadsförhållanden').select('IT bland individer')
        self.assertIn('Användning av dator', [x['text'] for x in self.scb.topics])
        self.scb.reset()

    def test_unselect_topic(self):
        self.scb.select('Miljö').unselect()
        self.assertIn('Offentlig ekonomi', [x['text'] for x in self.scb.topics])

    def test_fetch(self):
        self.scb.select('BE/BE0101/BE0101H/FoddaK', by_label=False)
        dataset = self.scb.fetch({
            'code':'Tid',
            'kind':'item',
            'values':['2014'],
            'format':'json'
        })
        self.assertIn('år', dataset.dimensions)
        self.assertIn('Levande födda', dataset.dimensions)
        self.assertEqual(dataset.data[1][2], '29496')
        self.scb.reset()


class TestSOS(unittest.TestCase):
    """Tests SOS scraper."""
    def setUp(self):
        self.sos = SOS()

    @unittest.skip("Expected failure")
    def test_list_topics(self):
        self.assertIn('Familjerätt', [x['text'] for x in self.sos.topics])

    @unittest.skip("Expected failure")
    def test_fetch(self):
        self.sos.get('Hjärtinfarkter')
        dataset = self.sos.fetch({
            'division': 'Fördelning på hemortslän',
            'indicator': 'Avlidna med någon akut hjärtinfarktdiagnos',
            'region': 'Stockholm',
            'age-from': '20-24 år',
            'age-to': '85- år',
            'gender': 'Män',
            'year': 2011
        })
        self.assertIn('Ålder', dataset.dimensions)
        self.assertEqual(dataset.data[5][1], 4)


class TestBRA(unittest.TestCase):
    """Tests BRA scraper."""
    def setUp(self):
        self.bra = BRA()

    @unittest.skip("Expected failure")
    def test_list_topics(self):
        self.assertIn('Handlagda brott', [x['text'] for x in self.bra.topics])

    @unittest.skip("Expected failure")
    def test_fetch(self):
        self.bra.get('Anmälda brott')
        dataset = self.bra.fetch({
            'crime': 'Sexualbrott, Blottning',
            'region': 'Arvika kommun',
            'unit': 'Antal brott',
            'period': ['År, 2013', 'År, 2012']
        })
        self.assertIn('crime', dataset.dimensions)
        self.assertEqual(dataset.data[1][0], 2)
