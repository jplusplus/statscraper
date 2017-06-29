# encoding: utf-8
""" Contains code for parsing datatypes from the statscraper-datatypes repo
"""

from glob import iglob
from itertools import chain
from csvkit import DictReader
import base_scraper  # FIXME move DimensionValue to avoid this import loop
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATATYPES_FILE = os.path.join(DIR_PATH, "datatypes", "datatypes.csv")


class NoSuchDatatype(Exception):
    """No datatype with that id."""

    pass


class Datatype(object):
    """Represent a datatype, initiated by id."""

    def __init__(self, id):
        """Id is a datatype from datatypes.csv."""
        self.id = id
        self.allowed_values = base_scraper.Valuelist()

        data = None
        with open(DATATYPES_FILE, 'rb') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                if row["id"] == id:
                    data = row
                    break
        if data is None:
            raise(NoSuchDatatype)
        self.value_type = data["value_type"]
        self.description = data["description"]
        domain = data["allowed_values"]
        if domain:
            for file_ in self._get_csv_files(domain):
                with open(file_, 'rb') as csvfile:
                    reader = DictReader(csvfile)
                    dialect_names = [x
                                     for x in reader.fieldnames
                                     if x.startswith("dialect:")]
                    for row in reader:
                        value = base_scraper.DimensionValue(row["id"],
                                                            self,
                                                            label=row["label"])
                        dialects = {
                            d[8:]: row[d].split(",")
                            for d in dialect_names
                        }
                        value.dialects = dialects
                        self.allowed_values.append(value)

    def _get_csv_files(self, domain):
        domain = os.path.join(*domain.split("/"))

        # We are fetching both by filename and dir name
        # so that regions/kenya will match anything in
        # `datatypes/values/regions/kenya/*.csv`
        # and/or `datatypes/values/regions/kenya.csv`
        #
        # There is probably an easier way to do this
        # FIXME the below function fetches /foo/bar/regions/kenya as well, but we probably want ^regions/kenya
        value_path_1 = os.path.join(DIR_PATH, "datatypes", "values", domain)
        value_path_2 = os.path.join(DIR_PATH, "datatypes", "values")
        files_1 = chain.from_iterable(iglob(os.path.join(root, '*.csv'))
                                      for root, dirs, files in os.walk(value_path_1))
        files_2 = chain.from_iterable(iglob(os.path.join(root, domain + '.csv'))
                                      for root, dirs, files in os.walk(value_path_2))
        for f in chain(files_1, files_2):
            yield f

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<Datatype: %s>' % str(self)
