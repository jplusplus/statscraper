==============
Using scrapers
==============

Every scraper built on Statscraper shares the same interface towards the user. Here's sample code using one of the included demo scrapers, to fetch the number of cranes spotted at Hornborgarsjön each day from `Länsstyrelsen i Västra Götalands län <http://web05.lansstyrelsen.se/transtat_O/transtat.asp>`_:

.. code:: python

  >>> from statscraper.scrapers import Cranes

  >>> scraper = Cranes()
  >>> scraper.items  # List available datasets
  [<Dataset: Number of cranes>]

  >>> dataset = scraper["Number of cranes"]
  >>> dataset.dimensions
  [<Dimension: date (Day of the month)>, <Dimension: month>, <Dimension: year>]

  >>> row = dataset.data[0]  # first row in this dataset
  >>> row
  <Result: 7 (value)>
  >>> row.dict
  {'value': '7', u'date': u'7', u'month': u'march', u'year': u'2015'}
  >>> row.int
  7
  >>> row.tuple
  ('7', {u'date': u'7', u'month': u'march', u'year': u'2015'})

  >>> df = dataset.data.pandas  # get this dataset as a Pandas dataframe


Exploring sites
---------------
Scrapers act like “cursors” that move around a hierarchy of datasets and collections of datasets. Collections and datasets are refered to as “items”.

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
    >>> scraper.items
    [<Collection: tym (Arbetsmarknaden)>, <Collection: vrm (Befolkning)>, ...]

    >>> scraper.move_to("vrm").move_to("synt").move_to("080_synt_tau_203.px")
    >>> scraper.current_item
    <Dataset: 080_synt_tau_203.px (Befolkningsförändringar efter område 1980 - 2016)>

    >>> scraper.move_up()
    >>> scraper.current_item
    <Collection: synt (Födda)>
    >>> scraper.move_to("010_synt_tau_101.px")
    >>> scraper.current_item
    <Dataset: 010_synt_tau_101.px (Summerat fruktsamhetstal för åren 1776 - 2016)>

    >>> scraper.move_to_top()
    >>> scraper.move_to(0)  # Moving by index works too


The datasets above could also be accessed like this:

.. code:: python

    >>> from statscraper.scrapers import PXWeb

    >>> scraper = PXWeb(base_url="http://pxnet2.stat.fi/pxweb/api/v1/sv/StatFin/")

    >>> collection = scraper["vrm"]["synt"]
    >>> collection
    <Collection: synt (Födda)>

    >>> dataset_1 = collection["080_synt_tau_203.px"]
    >>> dataset_2 = collection["010_synt_tau_101.px"]

At any given point, :code:`scraper["foo"]` is shorthand for :code:`scraper.current_item.items["foo"]`.

If you want to loop throuh every available dataset a scraper can offer, there is a :code:`Scraper.descendants` property that will recursively move to every item in the tree. Here is an example, that will find all datasets in the SCB API that has monthly data:

.. code:: python

    >>> from statscraper.scrapers import SCB

    >>> scraper = SCB()
    >>> for dataset in scraper.descendants:
    >>>     if dataset.dimensions["Tid"].label == u"månad":
    >>>         print "Ahoy! Dataset %s has monthly data!" % dataset

Exploring datasets
------------------

Much like itemslists (:code:`Collection.items`), datasets are only fetched when you are inspecting or interacting with them.

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

If you want to querry a site or database for some subset of the available data, you can use the :code:`fetch()` method on the dataset (or on the scraper, to fetch data from the current position, if any):

.. code:: python

    >>> dataset = scraper.items[0]
    >>> data = dataset.fetch(query={'year': "2017"})

or

.. code:: python

    >>> scraper.move_to(0)
    >>> data = scraper.fetch(query={'year': "2017"})

Available dimensions can be inspected though the .dimensions property:

.. code:: python

    >>> dataset.dimensions
    [<Dimension: date>, <Dimension: year>]

Note however that a scraper does not necessarily need to provide dimensions. If :code:`Dataset.dimensions` is None, it could simply mean that the scraper itself is not sure what to expect from the data.

Dialects
--------

Scraper authors can use the included :code:`Datatypes` module to have a standardised ontology for common statistical dimensions. If a dimensions uses a bulid in datatype, it can be translated to a different dialect. For instance, Swedish municipalities come in the following dialects:

 - :code:`short`: :code:`"Ale"`
 - :code:`numerical`: :code:`"1440"`
 - :code:`wikidata`: :code:`"Q498470"`
 - :code:`brå`: :code:`"8617"`
 - :code:`scb`: :code:`"1440 Ale kommun"`

By default, Statscraper prefers human readable representations, and municipality values is internally stored like this: :code:`u"Borås kommun"`. The philosophy here is that human readable id's speed up debugging and makes it easy to spot errors during scraping and analysis. Yes, we do use Unicode for id's. It's 2017 after all.

.. code:: python

    >>> from statscraper.scrapers import Cranes

    >>> scraper = Cranes()
    >>> data = scraper.items[0].data
    >>> row = data[0]
    >>> row["month"]
    <DimensionValue: march (month)>
    >>> row["month"].translate("swedish")
    u'mars'

For available datatypes, domains, values and dialects, see the `statscraper-datatypes repo <https://github.com/jplusplus/statscraper-datatypes>`_.
