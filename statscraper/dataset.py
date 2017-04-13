class Dataset():
    """A dataset."""
    def __init__(self, label, dimensions=None, measures=None):
        self.label = label
        self.dimensions = dimensions
        self.measures = measures

    def load(self, data):
        self.data = data
        return self

    def __repr__(self):
        return '<Dataset: {}>'.format(self.label)