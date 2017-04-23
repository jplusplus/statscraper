class Dataset():
    """A dataset."""
    def __init__(self, label, dimensions=None):
        self.label = label
        self.dimensions = dimensions

    def load(self, data):
        self.data = data
        return self

    @property
    def shape(self):
        """Computes the shape of the dataset as (rows, cols)."""
        if not self.data:
            return (0, 0)
        return (len(self.data), len(self.dimensions))

    def __repr__(self):
        return '<Dataset: {}>'.format(self.label)