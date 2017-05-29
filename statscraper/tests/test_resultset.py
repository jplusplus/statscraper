from unittest import TestCase

from base_scraper import ResultSet
from pandas.api import types as ptypes


class TestResultSet(TestCase):

    def pandas_export(self):
        result = ResultSet()
        result.append({'city': "Voi", 'value': 45483})
        df = result.pandas
        self.assertTrue(ptypes.is_numeric_dtype(df.value))
