import pandas as pd
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

    def _fetch_itemslist(self, item):
        """There's one dataset spread out in many files."""
        yield Dataset('Vehicles')

    def _fetch_dimensions(self, dataset):
        yield Dimension('month', datatype='month', dialect='swedish')
        yield Dimension('year', datatype='year')
        yield Dimension('vehicle')
        yield Dimension('measure')

    def _fetch_data(self, dataset, query=None):
        files = [(y, m) for y in query['years'] for m in query['months']]
        frames = []
        for file in files:
            url = self.BASE_URL.format(year=file[0], month=MONTHS[file[1]])
            frames.append(pd.read_excel(url))
        raw_data = pd.concat(frames)
        for i, row in raw_data.iterrows():
            yield Result(row['Unnamed: 1'], {
                            "avregistrerad": row['AVREGISTRERAD'],
                            "avställd": row['AVSTÄLLD'],
                            "itrafik": row['ITRAFIK']
                        })
