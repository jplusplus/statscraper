=================
API Documentation
=================

Documentation of statscraper's public API.


Main Interface
--------------

.. autoclass:: statscraper.BaseScraper
	:members:
.. autoclass:: statscraper.BaseScraperList
	:members: get
.. autoclass:: statscraper.BaseScraperObject
.. autoclass:: statscraper.Collection
.. autoclass:: statscraper.Dataset
.. autoclass:: statscraper.Dimension
.. autoclass:: statscraper.DimensionList
.. autoclass:: statscraper.DimensionValue
.. autoclass:: statscraper.Item
.. autoclass:: statscraper.Result
.. autoclass:: statscraper.ResultSet
.. autoclass:: statscraper.ValueList


Exceptions
--------------

.. autoclass:: statscraper.exceptions.DatasetNotInView
.. autoclass:: statscraper.exceptions.InvalidData
.. autoclass:: statscraper.exceptions.InvalidID
.. autoclass:: statscraper.exceptions.NoSuchDatatype
.. autoclass:: statscraper.exceptions.NoSuchItem