# encoding: utf-8

u"""
 This file contains the base class for scrapers. The scraper can navigate
 though an hierarchy of collections and datasets. Collections and datasets
 are refered to as “items”.

       ┏━ Collection ━━━ Collection ━┳━ Dataset
 ROOT ━╋━ Collection ━┳━ Dataset     ┣━ Dataset
       ┗━ Collection  ┣━ Dataset     ┗━ Dataset
                      ┗━ Dataset

 ╰───────────────────────┬─────────────────────╯
                     items

 A scraper can override three methods:
  * _fetch_itemslist(item) yields items at the current position
  * _fetch_dimensions(dataset) yields dimensions available on a dataset
  * _fetch_data(dataset) syield rows from a dataset

 A number of hooks are avaiable for more advanced scrapers. These are called
 by adding the on decorator on a method:

  @BaseScraper.on("up")
  def my_method(self):
    # Do something when the cusor moves up one level

"""
import six
from hashlib import md5
from json import dumps
import pandas as pd
from collections import deque
from copy import copy
from .exceptions import NoSuchItem, InvalidID
from .datatypes import Datatype
from .BaseScraperObject import BaseScraperObject
from .BaseScraperList import BaseScraperList
from .DimensionValue import DimensionValue
from .ValueList import ValueList

if six.PY3:
    unicode = str

try:
    from itertools import ifilter as filter
except ImportError:
    pass

TYPE_DATASET = "Dataset"
TYPE_COLLECTION = "Collection"
ROOT = "<root>"  # Special id for root position
VALUE_KEY = "value"  # key/column holding the value of a result or dimension
""" Constants for item types and id's """


class ResultSet(list):
    """The result of a dataset query.

    This is essentially a list of Result objects.
    """

    _pandas = None
    dataset = None

    @property
    def list_of_dicts(self):
        """Return a list of dictionaries, with the key "value" for values."""
        return [dict(x) for x in self]

    @property
    def pandas(self):
        """Return a Pandas dataframe."""
        if self._pandas is None:
            self._pandas = pd.DataFrame().from_records(self.list_of_dicts)
        return self._pandas

    def translate(self, dialect):
        """Return a copy of this ResultSet in a different dialect."""
        new_resultset = copy(self)
        new_resultset.dialect = dialect

        for result in new_resultset:
            for dimensionvalue in result.dimensionvalues:
                dimensionvalue.value = dimensionvalue.translate(dialect)
        return new_resultset

    def append(self, val):
        """Connect any new results to the resultset.

        This is where all the heavy lifting is done for creating results:
         - We add a datatype here, so that each result can handle
        validation etc independently. This is so that scraper authors
        don't need to worry about creating and passing around datatype objects.
         - As the scraper author yields result objects, we append them to
        a resultset.
         - This is also where we normalize dialects.
        """
        val.resultset = self
        val.dataset = self.dataset

        # Check result dimensions against available dimensions for this dataset
        if val.dataset:
            dataset_dimensions = self.dataset.dimensions
            for k, v in val.raw_dimensions.items():
                if k not in dataset_dimensions:
                    d = Dimension(k)
                else:
                    d = dataset_dimensions[k]

                # Normalize if we have a datatype and a foreign dialect
                normalized_value = unicode(v)
                if d.dialect and d.datatype:
                    if d.dialect in d.datatype.dialects:
                        for av in d.allowed_values:
                            # Not all allowed_value have all dialects
                            if unicode(v) in av.dialects.get(d.dialect, []):
                                normalized_value = av.value
                                # Use first match
                                # We do not support multiple matches
                                # This is by design.
                                break

                # Create DimensionValue object
                if isinstance(v, DimensionValue):
                    dim = v
                    v.value = normalized_value
                else:
                    if k in dataset_dimensions:
                        dim = DimensionValue(normalized_value, d)
                    else:
                        dim = DimensionValue(normalized_value, Dimension())

                val.dimensionvalues.append(dim)

            # Add last list of dimension values to the ResultSet
            # They will usually be the same for each result
            self.dimensionvalues = val.dimensionvalues

        super(ResultSet, self).append(val)


class DimensionList(BaseScraperList):
    """A one dimensional list of dimensions."""

    pass


class Result(BaseScraperObject):
    u"""A “row” in a result.

    A result contains a numerical value,
    and optionally a set of dimensions with values.
    """

    def __init__(self, value, dimensions={}):
        """Value is supposed, but not strictly required to be numerical."""
        self.value = value
        self.label = VALUE_KEY
        self.raw_dimensions = dimensions
        self.dimensionvalues = DimensionList()

    def __getitem__(self, key):
        """ Make it possible to get dimensions by name. """
        if isinstance(key, six.string_types):
            return self.dimensionvalues[key]
        else:
            return list.__getitem__(self, key)

    def __iter__(self):
        """ dict representation is like:
         {value: 123, dimension_1: "foo", dimension_2: "bar"}
        """
        yield (VALUE_KEY, self.value)
        for dv in self.dimensionvalues:
            yield (dv.id,
                   dv.value)

    @property
    def dict(self):
        return dict(self)

    @property
    def int(self):
        return int(self)

    @property
    def str(self):
        return str(int(self))

    @property
    def tuple(self):
        """ Tuple conversion to (value, dimensions), e.g.:
         (123, {dimension_1: "foo", dimension_2: "bar"})
        """
        return (self.value, {dv.id: dv.value for dv in self.dimensionvalues})


class Dimension(BaseScraperObject):
    """A dimension in a dataset."""

    def __init__(self, id_=None, label=None,
                 allowed_values=None, datatype=None,
                 dialect=None, domain=None):
        """A single dimension.

        If allowed_values are specified, they will override any
        allowed values for the datatype
        """
        if id_ is None:
            id_ = "default"
        if id_ == VALUE_KEY:
            raise InvalidID("'%s' is not a valid Dimension id." % VALUE_KEY)
        self.id = id_
        self._allowed_values = None
        self.datatype = None
        if label is None:
            self.label = id_
        else:
            self.label = label
        if datatype:
            self.datatype = Datatype(datatype)
            self._allowed_values = self.datatype.allowed_values
        self.dialect = dialect
        if allowed_values:
            # Override allowed values from datatype, if any
            #
            # If allowed values is given as a list of values, create
            # value objects using an empty dimension.
            self._allowed_values = ValueList()
            for val in allowed_values:
                if isinstance(val, DimensionValue):
                    self._allowed_values.append(val)
                else:
                    self._allowed_values.append(DimensionValue(val,
                                                               Dimension())
                                                )

    @property
    def allowed_values(self):
        """Return a list of allowed values."""
        if self._allowed_values is None:
            self._allowed_values = ValueList()
            for val in self.scraper._fetch_allowed_values(self):
                if isinstance(val, DimensionValue):
                    self._allowed_values.append(val)
                else:
                    self._allowed_values.append(DimensionValue(val,
                                                               Dimension()))
        return self._allowed_values


class ItemList(BaseScraperList):
    """A one dimensional list of items.

    Has some conventience getters and setters for scrapers
    """

    @property
    def type(self):
        """Check if this is a list of Collections or Datasets."""
        try:
            return self[0].type
        except IndexError:
            return None

    def empty(self):
        """Empty this list (delete all contents)."""
        del self[:]
        return self

    def append(self, val):
        """Connect any new items to the scraper."""
        val.scraper = self.scraper
        val._collection_path = copy(self.collection._collection_path)
        val._collection_path.append(val)
        super(ItemList, self).append(val)


class Item(BaseScraperObject):
    """Common base class for collections and datasets."""

    # These are populated when added to an itemlist
    parent = None  # Parent item
    _items = None  # ItemList with children
    _collection_path = None  # All ancestors

    def __init__(self, id_, label=None, blob=None):
        """Use blob to store any custom data."""
        self.id = id_
        self.blob = blob
        if label is None:
            self.label = id_
        else:
            self.label = label
        self._collection_path = deque([self])  # Will be overwritten when attached to an ItemList

    def _move_here(self):
        """Move the cursor to this item."""
        cu = self.scraper.current_item
        # Already here?
        if self is cu:
            return
        # A child?
        if cu.items and self in cu.items:
            self.scraper.move_to(self)
            return
        # A parent?
        if self is cu.parent:
            self.scraper.move_up()
        # A sibling?
        if self.parent and self in self.parent.items:
            self.scraper.move_up()
            self.scraper.move_to(self)
            return
        # Last resort: Move to top and all the way down again
        self.scraper.move_to_top()
        for step in self.path:
            self.scraper.move_to(step)

    @property
    def path(self):
        """All named collections above, including the current, but not root."""
        steps = list(self._collection_path)
        steps.pop(0)
        return steps

    @property
    def type(self):
        """Check if this is a Collection or Dataset."""
        try:
            if isinstance(self, Collection):
                return TYPE_COLLECTION
            else:
                return TYPE_DATASET
        except IndexError:
            return None


class Collection(Item):
    """A collection can contain collection of datasets.

    Lorem ipsum lorem lorem ipsum lorem. Dummy text.

    Basic Usage::

      >>> from statscraper import Collection
      >>> c = Collection()
      <class 'statscraper.base_scraper.Collection'>
    """

    @property
    def is_root(self):
        """Check if root element."""
        if self.id == ROOT:
            return True
        else:
            return None

    @property
    def items(self):
        """ItemList of children."""
        if self.scraper.current_item is not self:
            self._move_here()

        if self._items is None:
            self._items = ItemList()
            self._items.scraper = self.scraper
            self._items.collection = self
            for i in self.scraper._fetch_itemslist(self):
                i.parent = self
                if i.type == TYPE_DATASET and i.dialect is None:
                    i.dialect = self.scraper.dialect
                self._items.append(i)
        return self._items

    def __getitem__(self, key):
        """Provide bracket notation.

        collection["abc"] is shorthand for collection.items["abc"]
        """
        if self.scraper.current_item is not self:
            self._move_here()
        try:
            return self.items[key]
        except IndexError:
            # No such id
            raise NoSuchItem("No such item in Collection")

    def get(self, key):
        """Provide alias for bracket notation."""
        return self[key]


class Dataset(Item):
    """A dataset. Can be empty."""

    _data = None  # We store one ResultSet for each unique query
    _dimensions = None
    dialect = None
    query = None

    def __init__(self, id_, label=None, blob=None):
        super(Dataset, self).__init__(id_, label, blob)
        self._data = {}

    @property
    def items(self):
        """A dataset has no children."""
        return None

    @property
    def _hash(self):
        """Return a hash for the current query.

        This hash is _not_ a unique representation of the dataset!
        """
        dump = dumps(self.query, sort_keys=True)
        if isinstance(dump, str):
            dump = dump.encode('utf-8')
        return md5(dump).hexdigest()

    def fetch_next(self, query=None, **kwargs):
        """Generator to yield data one row at a time.
        Yields a Result, not the entire ResultSet. The containing ResultSet
        can be accessed through `Result.resultset`, but be careful not to
        manipulate the ResultSet until it is populated (when this generator
        is empty), or you may see unexpected results.
        """
        if query:
            self.query = query

        hash_ = self._hash
        if hash_ in self._data:
            for result in self._data[hash_]:
                yield result

        if self.scraper.current_item is not self:
            self._move_here()

        self._data[hash_] = ResultSet()
        self._data[hash_].dialect = self.dialect
        self._data[hash_].dataset = self
        for result in self.scraper._fetch_data(self,
                                               query=self.query,
                                               **kwargs):
            self._data[hash_].append(result)
            yield result

    def fetch(self, query=None, **kwargs):
        """Ask scraper to return data for the current dataset."""
        if query:
            self.query = query

        hash_ = self._hash
        if hash_ in self._data:
            return self._data[hash_]

        if self.scraper.current_item is not self:
            self._move_here()

        rs = ResultSet()
        rs.dialect = self.dialect
        rs.dataset = self
        for result in self.scraper._fetch_data(self,
                                               query=self.query,
                                               **kwargs):
            rs.append(result)
        self._data[hash_] = rs
        return self._data[hash_]

    @property
    def data(self):
        """Data as a property, given current query."""
        return self.fetch(query=self.query)

    @property
    def dimensions(self):
        """Available dimensions, if defined."""
        # First of all: Select this dataset
        if self.scraper.current_item is not self:
            self._move_here()

        if self._dimensions is None:
            self._dimensions = DimensionList()
            for d in self.scraper._fetch_dimensions(self):
                d.dataset = self
                d.scraper = self.scraper
                self._dimensions.append(d)
        return self._dimensions

    @property
    def shape(self):
        """Compute the shape of the dataset as (rows, cols)."""
        if not self.data:
            return (0, 0)
        return (len(self.data), len(self.dimensions))


class BaseScraper(Collection):
    """The base class for scrapers."""

    # Hooks
    _hooks = {
        'init': [],  # Called when initiating the class
        'up': [],  # Called when trying to go up one level
        'top': [],  # Called when moving to top level
        'select': [],  # Called when trying to move to a Collection or Dataset
    }

    dialect = None

    @classmethod
    def on(cls, hook):
        """Hook decorator."""
        def decorator(function_):
            cls._hooks[hook].append(function_)
            return function_
        return decorator

    def __repr__(self):
        return u'<Scraper: %s>' % self.__class__.__name__

    def __init__(self, *args, **kwargs):
        """Initiate with a ROOT collection on top."""
        self.current_item = Collection(ROOT)
        self.current_item.scraper = self
        self.root = self.current_item

        for f in self._hooks["init"]:
            f(self, *args, **kwargs)

    def __getitem__(self, key):
        """ Make scraper[a] shorthand for scraper.items[a]
        """
        return self.items[key]

    @property
    def items(self):
        """ItemList of collections or datasets at the current position.

        None will be returned in case of no further levels
        """
        return self.current_item.items

    def fetch(self, query=None, **kwargs):
        """Let the current item fetch it's data."""
        return self.current_item.fetch(query, **kwargs)

    @property
    def parent(self):
        """Return the item above the current, if any."""
        return self.current_item.parent

    @property
    def path(self):
        """All named collections above, including the current, but not root."""
        return self.current_item.path

    def move_to_top(self):
        """Move to root item."""
        self.current_item = self.root
        for f in self._hooks["top"]:
            f(self)
        return self

    def move_up(self):
        """Move up one level in the hierarchy, unless already on top."""
        if self.current_item.parent is not None:
            self.current_item = self.current_item.parent

        for f in self._hooks["up"]:
            f(self)
        if self.current_item is self.root:
            for f in self._hooks["top"]:
                f(self)
        return self

    def move_to(self, id_):
        """Select a child item by id (str), reference or index."""
        if self.items:
            try:
                self.current_item = self.items[id_]
            except (StopIteration, IndexError, NoSuchItem):
                raise NoSuchItem
            for f in self._hooks["select"]:
                f(self, id_)
        return self

    def _fetch_itemslist(self, item):
        """Must be overriden by scraper authors, to yield items.

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
        """Should be overriden by scraper authors, to yield dimensions."""
        from warnings import warn
        warn("This scraper has no method for fetching dimensions.",
             RuntimeWarning)
        return
        yield
        # raise Exception("This scraper has no method for fetching dimensions!")

    def _fetch_allowed_values(self, dimension):
        """Can be overriden by scraper authors, to yield allowed values."""
        if self.allowed_values is None:
            yield None
        for allowed_value in self.allowed_values:
            yield allowed_value

    def _fetch_data(self, dataset, query=None):
        """Must be overriden by scraper authors, to yield dataset rows."""
        raise Exception("This scraper has no method for fetching data!")

    @property
    def descendants(self):
        """Recursively return every dataset below current item."""
        for i in self.current_item.items:
            self.move_to(i)
            if i.type == TYPE_COLLECTION:
                for c in self.children:
                    yield c
            else:
                yield i
            self.move_up()

    @property
    def children(self):
        """Former, misleading name for descendants."""
        from warnings import warn
        warn("Deprecated. Use Scraper.descendants.", DeprecationWarning)
        for descendant in self.descendants:
            yield descendant


# Solve any circular dependencies here:

DimensionList._CONTAINS = Dimension
ValueList._CONTAINS = DimensionValue
ItemList._CONTAINS = Item
