# encoding: utf-8
""" Contains code for parsing datatypes from the statscraper-datatypes repo
"""

from glob import iglob
from itertools import chain
import os


class Datatype(object):
    """Represent a datatype, initiated by id."""

    allowed_values = []

    def __init__(self, id):
        """Id is a datatype from datatypes.csv."""
        self.id = id

        dir_path = os.path.dirname(os.path.realpath(__file__))
        value_path = os.path.join(dir_path, "datatypes", "values")
        files = chain.from_iterable(iglob(os.path.join(root, '*.csv'))
                                    for root, dirs, files in os.walk(value_path))

        for f in files:
            print("FILE", f)
        for root, dirs, files in os.walk("/home/leo/statscraper/statscraper/datatypes/values"):
            print root, dirs, files

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<Datatype: %s>' % str(self)
