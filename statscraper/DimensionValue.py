"""This file contanis a class representing a value in a dataset."""
from .BaseScraperObject import BaseScraperObject


class DimensionValue(BaseScraperObject):
    """The value for a dimension inside a Resultset."""

    def __init__(self, value, dimension, label=None):
        """Value can be any type. dimension is a Dimension() object."""
        self.value = value
        self._dimension = dimension
        self._label = label
        self._id = dimension.id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def dimension(self):
        return self._dimension

    @dimension.setter
    def dimension(self, value):
        self._dimension = value

    def translate(self, dialect):
        """Translate this value to a different dialect."""
        if self.dimension.datatype is None:
            raise Exception(f"""\
A value must belong to a dimension of a specific datatyp, to be translated. \
{self.dimension} does not have a datatype.""")
        dt = self.dimension.datatype
        if self.value not in dt.allowed_values:
            raise Exception(f"""\
{self.value} is not an allowed value for this datatype, and can not be translated.""")

        translations = dt.allowed_values[self.value]
        translation = ",".join([x.replace(",", "\\,")
                               for x in translations.dialects[dialect]])
        return translation
