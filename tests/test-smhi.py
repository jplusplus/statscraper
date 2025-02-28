"""Test SMHI scraper."""
from statscraper.scrapers import SMHI


def test_get_data():
    """We should be able to access a dataset by path."""
    print("SMHI")
    scraper = SMHI()
    api = scraper.get("Meteorological Observations")
    dataset = api["Lufttemperatur, min, 2 gånger per dygn, kl 06 och 18"]
    assert "station" in dataset.dimensions
    query = dict(period="corrected-archive", station=["Delsbo"])
    res = dataset.fetch(query)
    assert len(res)
    assert res[0].value is not None
