==============
Using scrapers
==============

.. NOTE::

   This documentation refers to version 1.0.0.dev1, a development version.
   There might be changes to the scraper interface before 1.0.0 is released.

Every scraper built on Statscraper shares the same interface towards the user. Here's sample code using one of the included scrapers, to fetch the number of cranes spotted at Hornborgarsjön each day:

.. code:: python

  >>> from statscraper.scrapers import Cranes

  >>> scraper = Cranes()
  >>> scraper.items  # List available datasets
  [<Dataset: Number of cranes>]

  >>> dataset = scraper["Number of cranes"]
  >>> dataset.dimensions
  [<Dimension: date (date)>]

  >>> row = dataset.data[0]  # first row in this dataset
  >>> row
  '15'
  >>> dict(row)
  {'date': '2010-07-23', 'value': '15'}
  >>> int(row)
  15
  >>> row.tuple
  (15, {'date': '2010-07-23'})

  >>> df = dataset.data.pandas  # get this dataset as a Pandas dataframe


Exploring sites
---------------
Scrapers act like “cursors” that move around a hierarchy of datasets and collections of dataset. Collections and datasets are refered to as “items”.

:: 

        ┏━ Collection ━━━ Collection ━┳━ Dataset
  ROOT ━╋━ Collection ━┳━ Dataset     ┣━ Dataset
        ┗━ Collection  ┣━ Dataset     ┗━ Dataset
                       ┗━ Dataset

  ╰─────────────────────────┬───────────────────────╯
                       items

The cursor is moved around the item tree as needed when you access properties or data, but you can also move manually around the items, if you want to be in full control. Some scrapers, e.g. those that need to fill out and post forms, or handle session data, might require that you move the cursor around manually. For most simple scrapers, e.g. those accessing an API, this should not be necessary.

Moving the cursor manually:

.. code:: python

    >>> from statscraper.scrapers import PXWeb

    >>> scraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")
    >>> scraper.move_to("Befolkning")\
    ...        .move_to(u"Födda")\
    ...        .move_to(u"Befolkningsförändringar efter område 1980 - 2016")
    >>> scraper.current_item
    <Dataset: Befolkningsförändringar efter område 1980 - 2016>
    >>> data_1 = scraper.fetch()

    >>> scraper.move_up()
    >>> scraper.current_item
    <Collection: Födda>
    >>> scraper.current_item.items
    [<Dataset: Summerat fruktsamhetstal för åren 1776 - 2016>, ...]

    >>> scraper.move_to(0)  # Moving by index works too
    >>> scraper.current_item
    <Dataset: Summerat fruktsamhetstal för åren 1776 - 2016>
    >>> scraper.current_item.items
    None
    >>> scraper.current_item.parent
    <Collection: Födda>
    >>> data_2 = scraper.fetch()

    >>> scraper.move_to_top()
    >>> scraper.current_item
    <Collection: <root>>


The above example could also be written like this:

.. code:: python

    >>> from statscraper.scrapers import PXWeb

    >>> scraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")

    >>> collection = scraper["Befolkning"][u"Födda"]
    >>> collection
    <Collection: Födda>
    >>> collection.items
    [<Dataset: Summerat fruktsamhetstal för åren 1776 - 2016>, ...]

    >>> data_1 = collection[u"Befolkningsförändringar efter område 1980 - 2016"].data
    >>> data_2 = collection[0].data  # Selecting the first dataset in this collection

scraper["Befolkning"] is shorthand for scraper.items["Befolkning"].

If you want to loop throuh every available dataset a scraper can offer, there is a `Scraper.descendants` property that will recursively move to every item in the tree. Here is an example, that will find all datasets in the SCB API that has monthly data:

.. code:: python

    >>> from statscraper.scrapers import SCB

    >>> scraper = SCB()
    >>> for dataset in scraper.descendants:
    >>>     if dataset.dimensions["Tid"].label == u"månad":
    >>>         print "Ahoy! Dataset %s has monthly data!" % dataset

Exploring datasets
------------------

Much like itemslists (Colleciton.items), datasets are only fetched when you are inspecting or interacting with them. 

The actual data is stored in a property called data:

.. code:: python

    >>> from statscraper.scrapers import Cranes

    >>> scraper = Cranes()
    >>> dataset = scraper.items[0]
    >>> for row in dataset.data:
    >>>     print "%s cranes were spotted on %s" % (row.value, row["date"])

The data property will hold a list of result objects. The list can be converted to a few other formats, e.g. a pandas dataframe:

.. code:: python

    >>> from statscraper.scrapers import Cranes

    >>> scraper = Cranes()
    >>> dataset = scraper.items[0]
    >>> df = dataset.data.pandas  # convert to pandas dataframe

If you want to querry a site or database for some subset of the available data, you can use the `fetch()` method on the dataset (or on the scraper, to fetch data from the current position, if any):

.. code:: python

    >>> dataset = scraper.items[0]
    >>> data = dataset.fetch(query={'year': "2017"})

or

.. code:: python

    >>> scraper.move_to(0)
    >>> data = scraper.fetch(query={'year': "2017"})

Available dimensions can be inspected though the .dimensions property:

.. code:: python

    >>> print dataset.dimensions
    [<Dimension: date (date)>, <Dimension: year (year)>]

Note however that a scraper does not necessarily need to provide (or might not have any information on) dimensions. If `Dataset.dimensions` is None, it could simply mean that the scraper does not know what to expect from the data.

A dimension object contains things like description, value type, allowed values, etc. 

Dialects
--------


