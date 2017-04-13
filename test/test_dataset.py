import unittest
import csv
from statscraper import Dataset
from statscraper import dimensions


class TestCSVData(unittest.TestCase):
    """
    Tests a site where the data
    is stored in CSV files.
    """
    def setUp(self):
        dims= {
          'id': dimensions.SourceId(),
          'namn': dimensions.SourceName(),
          'n': dimensions.SWEREF99X(),
          'e': dimensions.SWEREF99Y(),
          'kommunkod': dimensions.MunicipalityCode(),
          'kalltyp': dimensions.Custom(),
          'registrerad_datum': dimensions.Date()
        }
        measures = ['temp', 'matt_flode', 'bedomt_flode', 'ph', 'ledningsformaga']
        dataset = Dataset('Källor', measures=measures, dimensions=dims)
        self.dataset = dataset

    def test_label(self):
        self.assertTrue(self.dataset.label == 'Källor')

    def test_loading(self):
        csv_data = ('id;namn;n;e;kommunkod;kalltyp;registrerad_datum\n'
                    'AHM2008092501;"Mose källa";6687680;422966;1783;punktkälla;2010-08-27\n'
                    'AKR2006092701;"Boasjö";6251197;525879;1080;punktkälla;2006-12-20')
        data = csv.DictReader(csv_data.splitlines(), delimiter=';')
        records = [dict(x) for x in data]
        self.dataset.load(records)
        self.assertTrue('kalltyp' in self.dataset.data[0].keys())
        self.assertTrue(self.dataset.data[1]['id'] == 'AKR2006092701')
