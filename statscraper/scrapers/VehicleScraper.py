import pandas as pd
from statscraper import BaseScraper


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

    BASE_URL = ('https://www.transportstyrelsen.se/sv/vagtrafik/'
                'statistik-och-strada/Vag/Fordonsstatistik/{year}/'
                'fordonsstatistik-{month}-{year}/')

    def __init__(self):
        pass

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
            url = self.BASE_URL.format(year=file[0], month=file[1])
            frames.append(pd.read_excel(url))
        raw_data = pd.concat(frames)

        # TODO: Wrangle data to long format
        # TODO: Convert months to strings