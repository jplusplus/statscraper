from .exceptions import NoSuchItem


class BaseScraperList(list):
    """ Lists of dimensions, values, etc all inherit this class
    for some common convenience methods, such as get_by_label()
    """

    _CONTAINS = object

    def get(self, key):
        """Provide alias for bracket notation."""
        return self[key]

    def get_by_label(self, label):
        """ Return the first item with a specific label,
        or None.
        """
        return next((x for x in self if x.label == label), None)

    def __getitem__(self, key):
        """ Make it possible to get item by id or value identity."""
        if isinstance(key, str):
            def f(x):
                return (x.id == key)
        elif isinstance(key, self._CONTAINS):
            def f(x):
                return (x is key)
        else:
            return list.__getitem__(self, key)

        try:
            return next(iter(filter(f, self)))
        except StopIteration:
            # No such item
            raise NoSuchItem("No such %s: %s" % (self._CONTAINS.__name__, key))

    def __contains__(self, item):
        """ Make the 'in' keyword check for value/id """
        if isinstance(item, str):
            return bool(len(list(filter(lambda x: x.value == item, self))))
        else:
            return super(BaseScraperList, self).__contains__(item)
