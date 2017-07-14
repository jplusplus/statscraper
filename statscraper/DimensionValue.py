from .BaseScraperObject import BaseScraperObject


class DimensionValue(BaseScraperObject):
    """The value for a dimension inside a Resultset."""

    def __init__(self, value, dimension, label=None):
        """Value can be any type. dimension is a Dimension() object."""
        self.value = value
        # FIXME make these getter methods
        self.dimension = dimension
        self.label = label
        self.id = dimension.id

    def translate(self, dialect):
        translation = self.value
        if self.dimension.datatype is not None:
            dt = self.dimension.datatype
            if self.value in dt.allowed_values:
                translations = dt.allowed_values[self.value]
                translation = (",").join(translations.dialects[dialect].replace(",", "\,"))
        return translation