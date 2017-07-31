# encoding: utf-8
from unittest import TestCase

from statscraper.scrapers.SMHIScraper import SMHI, Collection, API, SMHIDataset, Station


class TestSMHI(TestCase):

    def setUp(self):
        """Setting up scraper."""

    def test_fetch_api(self):
        scraper = SMHI()
        apis = scraper.items
        self.assertTrue(len(apis) > 0)
        api = apis[0]
        self.assertTrue(api, API)

        self.assertFalse(api.label is None)
        self.assertFalse(api.url is None)
        self.assertTrue(isinstance(api.json, dict))



    def test_fetch_dataset(self):
        u"""Moving to an “API”."""
        scraper = SMHI()
        api = scraper.get("Meteorological Observations")
        for dataset in api:
            self.assertFalse(dataset.label is None)
            self.assertFalse(dataset.url is None)
            # Make sure its a dataset
            self.assertTrue(isinstance(dataset, SMHIDataset))
            # Get dimensions
            self.assertEqual(len(dataset.dimensions), 4)

    def test_fetch_allowed_values(self):
        scraper = SMHI()
        api = scraper.get("Meteorological Observations")
        dataset = api.items[0]
        stations = dataset.dimensions["station"].allowed_values
        active_stations = [x for x in dataset.dimensions["station"].active_stations()]
        self.assertTrue(len(stations)>0)
        self.assertTrue(len(active_stations)>0)

        station = dataset.dimensions["station"].allowed_values.get_by_label(u"Växjö A")
        self.assertTrue(isinstance(station, Station))

        self.assertFalse(station.label is None)



        periods = dataset.dimensions["period"].allowed_values
        self.assertEqual(len(periods),4)


    def test_query(self):
        scraper = SMHI()
        api = scraper.get("Meteorological Observations")
        dataset = api.items[0]
        data = dataset.fetch({"station": u"Växjö A", "period": "latest-months"})
        self.assertTrue(len(data) > 0)



