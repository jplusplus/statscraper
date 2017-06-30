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

  >>> dataset = scraper.items["Number of cranes"]
  >>> dataset.dimensions
  [<Dimension: date (date)>]

  >>> dataset.data[0]  # first row in this dataset
  {'date': '2010-07-23', 'value': '15'}

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

    >>> collection = scraper.items["Befolkning"].items[u"Födda"]
    >>> collection
    <Collection: Födda>
    >>> collection.items
    [<Dataset: Summerat fruktsamhetstal för åren 1776 - 2016>, ...]

    >>> data_1 = collection.items[u"Befolkningsförändringar efter område 1980 - 2016"].data
    >>> data_2 = collection.items[0].data  # Selecting the first dataset in this collection


Exploring datasets
------------------


Querying datasets (fething data)
--------------------------------


Dialects
--------


