from unittest import TestCase

from statscraper import ResultSet
from pandas.api import types as ptypes


class TestResultSet(TestCase):

    def test_pandas_export(self):
        result = ResultSet()
        result.append({'city': "Voi", 'value': 45483})
        df = result.pandas
        self.assertTrue(ptypes.is_numeric_dtype(df.value))
