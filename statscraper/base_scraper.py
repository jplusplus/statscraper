# encoding: utf-8

"""
 This file contains the base class for scrapers. The scraper can navigate
 though an hierarchy of collections and datasets. Collections and datasets
 are refered to as “items”.

       ┏━ Collection ━━━ Collection ━┳━ Dataset
 ROOT ━╋━ Collection ━┳━ Dataset     ┣━ Dataset
       ┗━ Collection  ┣━ Dataset     ┗━ Dataset
                      ┗━ Dataset

 ╰─────────────────────────┬───────────────────────╯
                      items

 A scraper can override three methods:
  * _fetch_itemslist(item) yields items at the current position
  * _fetch_dimensions(dataset) yields dimensions available on a dataset
  * _fetch_data(dataset) syield rows from a dataset

 A number of hooks are avaiable for more advanced scrapers. These are called
 by adding the on decorator on a method:

  @on("up")
  def my_method(self):
    # Do something when the user moves up one level

"""
from hashlib import md5
from json import dumps
import pandas as pd

TYPE_DATASET = "Dataset"
TYPE_COLLECTION = "Collection"
ROOT = "<root>"  # Special id for root position
""" Constants for item types and id's """


class NoSuchItem(IndexError):
    """ No such Collection or Dataset """
    pass


class InvalidData(Exception):
    """ The scraper encountered some invalid data """
    pass


class ResultSet(list):
    """ The result of a dataset query
    """
    _pandas = None

    @property
    def pandas(self):
        """ Return a Pandas dataframe
        """
        if self._pandas is None:
            self._pandas = pd.DataFrame().from_records(self)
        return self._pandas


class Itemslist(list):
    """ A one dimensional list of items,
     with some conventience getters and setters for scrapers
    """

    @property
    def type(self):
        """ Check if this is a list of Collections or Datasets """
        try:
            return self[0].type
        except IndexError:
            return None

    def get(self, key):
        """
         Make it possible to get item by id
        """
        try:
            val = filter(lambda x: key == x.id, self).pop()
            return val
        except IndexError:
            # No such id
            raise KeyError("No such item in Itemslist")

    def empty(self):
        """ Empty this list (delete all contents) """
        del self[:]
        return self

    def append(self, val):
        """ Connect any new items to the scraper """
        val.scraper = self.scraper
        super(Itemslist, self).append(val)


class AllowedValue(object):
    """ An allowed value for a dimension """
    def __init__(self, value, label):
        self.value = value
        self.label = label or unicode(value)

    def __str__(self):
        try:
            return self.value.encode("utf-8")
        except UnicodeEncodeError:
            return self.value

    def __repr__(self):
        return '<Value: %s (%s)>' % (str(self), self.label.encode("utf-8"))


class Dimension(object):
    """ A dimension in a dataset """
    def __init__(self, id_, label=None, allowed_values=None, type=None):
        self.id = id_
        self.allowed_values = allowed_values
        if label is None:
            self.label = id_
        else:
            self.label = label

    def __str__(self):
        try:
            return self.id.encode("utf-8")
        except UnicodeEncodeError:
            return self.id

    def __repr__(self):
        return '<Dimension: %s (%s)>' % (str(self), self.label.encode("utf-8"))

    @property
    def values(self):
        """ Return a list of allowed values """
        if self.allowed_values is None:
            self.allowed_values = self.scraper._fetch_allowed_values(self)
        return self.allowed_values


class Item(object):
    """ Common base class for collections and datasets """
    def __init__(self, id_, blob=None):
        self.id = id_
        self.blob = blob

    def __str__(self):
        try:
            return self.id.encode("utf-8")
        except UnicodeEncodeError:
            return self.id

    @property
    def type(self):
        """ Check if this is a list of Collections or Datasets """
        try:
            if isinstance(self, Collection):
                return TYPE_COLLECTION
            else:
                return TYPE_DATASET
        except IndexError:
            return None


class Collection(Item):
    """ A collection can contain either a number of other
        collections or datasets.
        `id` should be Unicode, utf-8
    """

    def __repr__(self):
        return '<Collection: %s>' % str(self)

    @property
    def is_root(self):
        if self.id == ROOT:
            return True
        else:
            return None


class Dataset(Item):
    """ A dataset. Can be empty """
    _data = {}  # We store one ResultSet for each unique query
    query = None
    _dimensions = None

    @property
    def _hash(self):
        """ Return a hash for the current query.
            This hash is _not_ a unique representation of the dataset!
        """
        return md5(dumps(self.query, sort_keys=True)).hexdigest()

    def fetch(self, query=None):
        """ Ask the scraper to return data for the current dataset
        """
        # First of all: Select this dataset
        if self.scraper.current_item is not self:
            self.scraper.select(self)
        # Fetch can be called multiple times with different queries
        hash_ = self._hash
        if hash_ not in self._data:
            self._data[hash_] = ResultSet()
            for row in self.scraper._fetch_data(self, query=query):
                self._data[hash_].append(row)
        return self._data[hash_]

    @property
    def data(self):
        return self.fetch(query=self.query)

    @property
    def dimensions(self):
        if self._dimensions is None:
            self._dimensions = []
            for d in self.scraper._fetch_dimensions(self):
                d.dataset = self
                d.scraper = self.scraper
                self._dimensions.append(d)
        return self._dimensions

    @property
    def shape(self):
        """Computes the shape of the dataset as (rows, cols)."""
        if not self.data:
            return (0, 0)
        return (len(self.data), len(self.dimensions))

    def __repr__(self):
        return '<Dataset: %s>' % str(self)


class BaseScraper(object):
    """ The base class for scapers """

    # _items  # List of collections or datasets at current position
    # _collection_path  # All the parents of the current position

    current_item = Collection(ROOT)  # Current collection or dataset object

    # Hooks
    _hooks = {
        'init': [],  # Called when initiating the class
        'up': [],  # Called when trying to go up one level
        'select': [],  # Called when trying to select a Collection or Dataset
    }

    @classmethod
    def on(class_, hook):
        def decorator(function_):
            class_._hooks[hook].append(function_)
            return function_
        return decorator

    def __repr__(self):
        return u'<Scraper: %s>' % self.__class__.__name__

    def __init__(self, *args, **kwargs):
        self._items = Itemslist()
        self._items.scraper = self
        self._collection_path = []
        for f in self._hooks["init"]:
            f(self, *args, **kwargs)

    @property
    def items(self):
        """ View the collections or datasets at the current position,
            or None, if no further items. """
        if self.current_item.type == TYPE_DATASET:
            return None

        if len(self._items) == 0:
            for i in self._fetch_itemslist(self.current_item):
                self._items.append(i)
        return self._items

    @property
    def parent(self):
        """ Return the item above the current, if any """
        if len(self._collection_path) > 1:
            return self._collection_path[-2]
        else:
            return None

    def up(self):
        """ Move up one level in the hierarchy, unless already on top"""
        try:
            self._collection_path.pop()
            self.current_item = self._collection_path[-1]
        except IndexError:
            self.current_item = Collection(ROOT)
        self._items.empty()  # FIXME cache us?
        for f in self._hooks["up"]:
            f(self)
        return self

    def select(self, id_):
        """ Select an item by id (str), or dataset """
        try:
            # Move cursor to new item, and reset the cached list of subitems
            if isinstance(id_, basestring):
                def f(x): return (x.id == id_)
            elif isinstance(id_, Item):
                def f(x): return (x is id_)
            else:
                raise StopIteration
            self.current_item = filter(f, self.items).pop()
            self._collection_path.append(self.current_item)
            self._items.empty()
        except StopIteration:
            raise NoSuchItem
        print self._hooks
        for f in self._hooks["select"]:
            f(self)
        return self

    def _fetch_itemslist(self, item):
        """
         Should yield items (Collections or Datasets) at the
         current cursor position. E.g something like this:

         list = get_items(self.current_item)
         for item in list:
             if item.type == "Collection":
                 yield Collection(item.id)
             else:
                 yield Dataset(item.id)
        """
        raise Exception("This scraper has no method for fetching list items!")

    def _fetch_dimensions(self, dataset):
        """ Should yield dimensions used in a dataset.
        """
        raise Exception("This scraper has no method for fetching dimensions!")

    def _fetch_allowed_values(self, dimension):
        """ Can be used the fetch allowed values for a dimension, if those
            were not known when the dimension was created
        """
        return None

    def _fetch_data(self, dataset, query=None):
        """ Should yield dataset rows
        """
        raise Exception("This scraper has no method for fetching data!")
