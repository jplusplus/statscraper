import six


class BaseScraperObject(object):
    """ Objects like items, dimensions, values etc all inherit
    this class. BaseScraperObjects are typicalliy stored in a
    BaseScraperList.
    """

    def get(self, key):
        """Provide alias for bracket notation."""
        return self[key]

    @property
    def value(self):
        """ This is the value used for testing membership,
        comparison, etc. Overloaded for classes that store
        a value separate from the id, e.g. DimensionValue,
        that might have something like {id: 'year', value: 2017}
        """
        if hasattr(self, '_value'):
            return self._value
        else:
            return self.id

    @value.setter
    def value(self, value):
        """ This is the value used for testing membership,
        comparison, etc. Overloaded for classes that store
        a value separate from the id, e.g. DimensionValue,
        that might have something like {id: 'year', value: 2017}
        """
        self._value = value

    def __eq__(self, other):
        """ Enable equality check by string """
        if self is other:
            return True
        elif isinstance(other, six.string_types):
            return (self.value == other)
        else:
            return super(BaseScraperObject, self) == other

    def __nonzero__(self):
        """ Make nonezero check value """
        return bool(self.value)

    def __len__(self):
        """ Make len check value """
        return len(self.value)

    def __int__(self):
        """ Make int return value """
        return int(self.value)

    def __str__(self):
        if isinstance(self.value, six.string_types):
            try:
                if six.PY2:
                    return self.value.encode("utf-8")
                else:
                    return self.value
            except (UnicodeEncodeError, UnicodeDecodeError):
                return self.value
        else:
            return str(self.value)

    def __repr__(self):
        if self.label is None:
            label = self.id
        else:
            label = self.label.encode("utf-8")
        if str(self) != str(label):
            return '<%s: %s (%s)>' % (type(self).__name__,
                                      str(self),
                                      label)
        else:
            return '<%s: %s>' % (type(self).__name__,
                                 str(self))
