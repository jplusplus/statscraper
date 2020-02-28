"""Test SCB/PXWeb scraper."""
from statscraper.scrapers import SCB


def test_get_data():
    """We should be able to access a dataset by path."""
    scraper = SCB()
    scraper.move_to("HE").move_to("HE0110").move_to("HE0110F").move_to("Tab1DispInkN")
    data = scraper.fetch({
      "ContentsCode": ("item", "000002VY"),
      "InkomstTyp": ("item", "FastInkIn"),
    }, by="municipality")

    assert "Region" in data.dataset.dimensions
    assert "InkomstTyp" in data.dataset.dimensions

    df = data.pandas
    assert "value" in df.columns
    assert "Region" in df.columns
    assert "InkomstTyp" in df.columns