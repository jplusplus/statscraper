# encoding: utf-8

import pandas as pd
import json
from statscraper import BaseScraper, Dataset, Dimension, Result

MONTHS = ['januari', 'februari', 'mars', 'april', 'maj', 'juni'
          'juli', 'augusti', 'september', 'oktober', 'november', 'december']


class Vehicles(BaseScraper):
    """Vehicle statistics from Transportstyrelsen.

    :return: :class:`Vehicles <Vehicles>` object
    :rtype: statscraper.BaseScraper

    Usage::

      >>> from statscraper.scrapers import Vehicles
      >>> scraper = Vehicles()
      >>> scraper.items
      # [<Dataset: Vehicles>]
    """

    BASE_URL = ('https://www.transportstyrelsen.se/globalassets/'
                'global/press/statistik/fordonsstatistik/{year}/'
                'fordonsstatistik-{month}-{year}.xlsx')

    def _clean_data(self, df, year, month):
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all', axis=0)
        df = df.drop('Totalsumma', axis=1)
        df = df.rename(columns={'Unnamed: 1': 'vehicle_type'})
        df = df[df['vehicle_type'] != 'Totalsumma']
        df.loc[:, 'year'] = year
        df.loc[:, 'month'] = month
        df = pd.melt(df,
                     id_vars=['vehicle_type', 'month', 'year'],
                     value_vars=['AVREGISTRERAD', 'AVSTÄLLD', 'ITRAFIK'],
                     var_name='status')
        return df

    def _fetch_itemslist(self, item):
        """There's one dataset spread out in many files."""
        yield Dataset('Vehicles')

    def _fetch_dimensions(self, dataset):
        yield Dimension('year', datatype='year')
        yield Dimension('month')  # TODO: Convert to datatype month
        yield Dimension('vehicle_type')
        yield Dimension('status')

    def _fetch_data(self, dataset, query=None):
        files = [(y, m) for y in query['years'] for m in query['months']]
        frames = []

        # Download and clean every monthly Excel file
        for file in files:
            year, month = file
            url = self.BASE_URL.format(year=year, month=MONTHS[month])
            frame = self._clean_data(pd.read_excel(url), year, month)
            frames.append(frame)

        # Yield individual rows of type Result from the dataframe
        raw_data = pd.concat(frames)
        for i, row in raw_data.iterrows():
            val = row.pop('value')
            yield Result(val, json.loads(row.to_json()))
