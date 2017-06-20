from unittest import TestCase

from statscraper import Result, ResultSet
from pandas.api import types as ptypes


class TestResultSet(TestCase):

    def test_pandas_export(self):
        """Get results as pandas dataframe."""
        result = ResultSet()
        result.append(Result(45483, {'city': "Voi"}))
        df = result.pandas
        self.assertTrue(ptypes.is_numeric_dtype(df.value))
