from .BaseScraperList import BaseScraperList
from .DimensionValue import DimensionValue
from .exceptions import NoSuchItem


class ValueList(BaseScraperList):
    """A list of dimension values.

    allowed_values uses this class, to allow checking membership.
    """

    def __getitem__(self, key):
        """Make it possible to get value by value or value identity."""
        if isinstance(key, str):
            def f(x):
                return (x.value == key)
        elif isinstance(key, DimensionValue):
            def f(x):
                return (x is key)
        else:
            return list.__getitem__(self, key)
        try:
            val = next(iter(filter(f, self)))
            return val
        except IndexError:
            # No such id
            raise NoSuchItem("No such value")

    def __contains__(self, item):
        """ in should look for value, not id. """
        if isinstance(item, str):
            return bool(len(list(filter(lambda x: x.value == item, self))))
        else:
            return super(ValueList, self).__contains__(item)
