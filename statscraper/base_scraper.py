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

  @on("up")
  def my_method(self):
    # Do something when the cusor moves up one level

"""
import six
from hashlib import md5
from json import dumps
import pandas as pd
from collections import deque
from copy import copy
from .datatypes import Datatype

try:
    from itertools import ifilter as filter
except ImportError:
    pass

TYPE_DATASET = "Dataset"
TYPE_COLLECTION = "Collection"
ROOT = "<root>"  # Special id for root position
""" Constants for item types and id's """


class NoSuchItem(IndexError):
    """No such Collection or Dataset."""

    pass


class DatasetNotInView(IndexError):
    """Tried to operate on a dataset that is not visible.

    This can be raised by a scraper if the cursor needs to
    move before inspecting an item.
    """

    pass


class InvalidData(Exception):
    """The scraper encountered some invalid data."""

    pass


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
                return self.value.encode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                return self.value
        else:
            return str(self.value)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, str(self))


class BaseScraperList(list):
    """ Lists of dimensions, values, etc all inherit this class
    for some common convenience methods, such as get_by_label()
    """

    _CONTAINS = object

    def get(self, key):
        """Provide alias for bracket notation."""
        return self[key]

    def get_by_label(self, label):
        """ Return the first item with a specific label,
        or None.
        """
        return next((x for x in self if x.label == label), None)

    def __getitem__(self, key):
        """ Make it possible to get item by id or value identity."""
        if isinstance(key, six.string_types):
            if isinstance(key, unicode):
                def f(x):
                    return (x.id == key)
            else:
                def f(x):
                    return (x.id == unicode(key, encoding="utf-8"))
        elif isinstance(key, self._CONTAINS):
            def f(x):
                return (x is key)
        else:
            return list.__getitem__(self, key)

        try:
            return next(filter(f, self))
        except StopIteration:
            # No such item
            raise NoSuchItem("No such %s: %s" % (self._CONTAINS.__name__, key))

    def __contains__(self, item):
        """ Make the 'in' keyword check for value/id """
        if isinstance(item, six.string_types):
            return bool(len(list(filter(lambda x: x.value == item, self))))
        else:
            return super(BaseScraperList, self).__contains__(item)


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

        We will also add a datatype here, so that each result can handle
        validation etc independently. This is so that scraper authors
        don't need to worry about creating and passing around datatype objects.

        As the scraper author yields result objects, we append them to
        a resultset.

        This is also where we normalize dialects.
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
                normalized_value = str(v)
                if d.dialect and d.datatype:
                    if d.dialect in d.datatype.dialects:
                        for av in d.allowed_values:
                            if str(v) in av.dialects[d.dialect]:
                                normalized_value = av.value
                                # Use first match
                                # We do not support multiple values
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

        super(ResultSet, self).append(val)


class Dimensionslist(BaseScraperList):
    """A one dimensional list of dimensions."""

    pass


class Result(BaseScraperObject):
    u"""A “row” in a result.

    A result contains a numerical value,
    and optionlly a set of dimensions with values.
    """

    def __init__(self, value, dimensions={}):
        """Value is supposed, but not strictly required to be numerical."""
        self.value = value
        self.raw_dimensions = dimensions
        self.dimensionvalues = Dimensionslist()

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
        yield ("value", self.value)
        for dv in self.dimensionvalues:
            yield (dv.id,
                   dv.value)

    @property
    def dict(self):
        return dict(self)

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
                 dialect=None):
        """A single dimension.

        If allowed_values are specified, they will override any
        allowed values for the datatype
        """
        if id_ is None:
            id_ = "default"
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
            self._allowed_values = Valuelist()
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
            self._allowed_values = Valuelist()
            for val in self.scraper._fetch_allowed_values(self):
                if isinstance(val, DimensionValue):
                    self._allowed_values.append(val)
                else:
                    self._allowed_values.append(DimensionValue(val,
                                                               Dimension()))
        return self._allowed_values


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
                translation = (", ").join(translations.dialects[dialect])
        return translation


class Valuelist(BaseScraperList):
    """A list of dimension values.

    allowed_values uses this class, to allow checking membership.
    """

    def __getitem__(self, key):
        """Make it possible to get value by value or value identity."""
        if isinstance(key, six.string_types):
            if isinstance(key, unicode):
                def f(x):
                    return (x.value == key)
            else:
                def f(x):
                    return (x.value == unicode(key, encoding="utf-8"))
        elif isinstance(key, DimensionValue):
            def f(x):
                return (x is key)
        else:
            return list.__getitem__(self, key)
        try:
            val = next(filter(f, self))
            return val
        except IndexError:
            # No such id
            raise NoSuchItem("No such value")

    def __contains__(self, item):
        """ in should look for value, not id. """
        if isinstance(item, six.string_types):
            return bool(len(list(filter(lambda x: x.value == item, self))))
        else:
            return super(Valuelist, self).__contains__(item)


class Itemslist(BaseScraperList):
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
        super(Itemslist, self).append(val)


class Item(BaseScraperObject):
    """Common base class for collections and datasets."""

    # These are populated when added to an itemlist
    parent = None  # Parent item
    _items = None  # Itemslist with children
    _collection_path = None  # All ancestors

    def __init__(self, id_, label=None, blob=None):
        """Use blob to store any custom data."""
        self.id = id_
        self.blob = blob
        if label is None:
            self.label = id_
        else:
            self.label = label
        self._collection_path = deque([self])  # Will be overwritten when attached to an Itemslist

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
    """A collection can contain collection of datasets."""

    def __repr__(self):
        return '<Collection: %s>' % str(self)

    @property
    def is_root(self):
        """Check if root element."""
        if self.id == ROOT:
            return True
        else:
            return None

    @property
    def items(self):
        """Itemslist of children."""
        if self.scraper.current_item is not self:
            self._move_here()

        if self._items is None:
            self._items = Itemslist()
            self._items.scraper = self.scraper
            self._items.collection = self
            for i in self.scraper._fetch_itemslist(self):
                i.parent = self
                if i.type == TYPE_DATASET and i.dialect is None:
                    i.dialect = self.scraper.dialect
                self._items.append(i)
        return self._items

    def __getitem___(self, key):
        """Provide  bracket notation.

        collection["abc"] till return the item with id abc
        """
        if self.scraper.current_item is not self:
            self._move_here()
        try:
            return next(filter(lambda x: x.id == key, self.items))
        except IndexError:
            # No such id
            raise NoSuchItem("No such item in Collection")

    def get(self, key):
        """Provide alias for bracket notation."""
        return self[key]


class Dataset(Item):
    """A dataset. Can be empty."""

    _data = {}  # We store one ResultSet for each unique query
    _dimensions = None
    dialect = None
    query = None

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

    def fetch(self, query=None):
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
        for result in self.scraper._fetch_data(self, query=self.query):
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
            self._dimensions = Dimensionslist()
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

    def __repr__(self):
        return '<Dataset: %s>' % str(self)


class BaseScraper(object):
    """The base class for scapers."""

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

    @property
    def items(self):
        """Itemslist of collections or datasets at the current position.

        None will be returned in case of no further levels
        """
        return self.current_item.items

    def fetch(self, query=None):
        """Let the current item fetch it's data."""
        return self.current_item.fetch(query)

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
                # Move cursor to new item, and reset the cached list of subitems
                self.current_item = self.items[id_]
            except (StopIteration, IndexError, NoSuchItem):
                raise NoSuchItem
            for f in self._hooks["select"]:
                f(self)
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

Dimensionslist._CONTAINS = Dimension
Valuelist._CONTAINS = DimensionValue
Itemslist._CONTAINS = Item
