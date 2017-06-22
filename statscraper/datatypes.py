# encoding: utf-8
""" Contains code for parsing datatypes from the statscraper-datatypes repo
"""


class Datatype(object):
    """Represent a datatype, initiated by id."""

    allowed_values = []

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<Datatype: %s>' % str(self)
