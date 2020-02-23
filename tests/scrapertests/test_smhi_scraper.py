# encoding: utf-8
from unittest import TestCase
import pandas as pd
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
            self.assertGreater(len(dataset.dimensions), 0)

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
        self.assertEqual(len(periods), 4)


    def test_query(self):
        scraper = SMHI()
        api = scraper.get("Meteorological Observations")
        dataset = api.items[0]
        data = dataset.fetch({"station": u"Växjö A", "period": "latest-months"})
        self.assertTrue(len(data) > 0)


    def test_get_stations_list(self):
        scraper = SMHI()
        api = scraper.get("Meteorological Observations")
        dataset = api.items[0]
        stations = dataset.get_stations_list()
        self.assertTrue(len(stations) > 0)
        for station in stations:
            self.assertTrue("longitude" in station)

        active_stations = dataset.get_active_stations_list()

        self.assertTrue(len(active_stations) > 0)
        self.assertTrue(len(stations) > len(active_stations))

    def test_iterate_queries(self):
        # Make same query to multiple datasets
        scraper = SMHI()
        api = scraper.get("Meteorological Observations")
        datasets = [
            u"Nederbördsmängd, summa, 1 gång per månad",
            u"Lufttemperatur, medel, 1 gång per månad",
        ]
        dfs = []
        for dataset_name in datasets:
            query = {
                "period": ["corrected-archive"],
                "station": "Abisko"
            }

            res = api.get(dataset_name).fetch(query)
            dfs.append(res.pandas)

        # Merge the two resultsets to one dataframe
        df = pd.concat(dfs)

        # Make sure that both parameters (datasets) are in
        # the final dataframe
        parameters = df["parameter"].unique()
        self.assertTrue(len(parameters) == 2)
        for parameter in parameters:
            self.assertTrue(parameter in datasets)
