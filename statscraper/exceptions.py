class InvalidID(Exception):
    """This string is not allowed as an id at this point.
    Note: Inherits from Exception instead of StandardError
    for Python3.x compatibility reasons."""

    pass


class NoSuchItem(IndexError):
    """No such Collection or Dataset."""

    pass


class DatasetNotInView(IndexError):
    """Tried to operate on a dataset that is not visible.

    This can be raised by a scraper if the cursor needs to
    move before inspecting an item.
    """

    pass


class InvalidData(Exception):
    """The scraper encountered some invalid data."""

    pass


class NoSuchDatatype(Exception):
    """No datatype with that id."""

    pass
