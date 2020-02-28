"""Test datatypes."""
from statscraper.datatypes import Datatype
from statscraper import Dimension, DimensionValue


def test_allowed_values():
    """Datatypes shuold have allowed values."""
    dt = Datatype("region")
    assert("Ale kommun" in dt.allowed_values)


def test_b():
    """Dimension values should be translatable."""
    d = Dimension("municipality", datatype="region", domain="sweden/municipalities")
    dv = DimensionValue("Ale kommun", d)
    assert(dv.translate("numerical") == "1440")
