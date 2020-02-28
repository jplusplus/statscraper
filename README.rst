Statscraper is a base library for building web scrapers for statistical data, with a helper ontology for (primarily Swedish) statistical data. A set of ready-to-use scrapers are included.

For users
=========

You can use Statscraper as a foundation for your next scraper, or try out any of the included scrapers. With Statscraper comes a unified interface for scraping, and some useful helper methods for scraper authors.

Full documentation: ReadTheDocs_

For updates and discussion: Facebook_

By `Journalism++ Stockholm <http://jplusplus.org/sv>`_, and Robin Linderborg.

Installing
----------

.. code:: bash

  pip install statscraper

Using a scraper
---------------
Scrapers acts like “cursors” that move around a hierarchy of datasets and collections of datasets. Collections and datasets are refered to as “items”.

::

        ┏━ Collection ━━━ Collection ━┳━ Dataset
  ROOT ━╋━ Collection ━┳━ Dataset     ┣━ Dataset
        ┗━ Collection  ┣━ Dataset     ┗━ Dataset
                       ┗━ Dataset

  ╰─────────────────────────┬───────────────────────╯
                       items

Here's a simple example, with a scraper that returns only a single dataset: The number of cranes spotted at Hornborgarsjön each day as scraped from `Länsstyrelsen i Västra Götalands län <http://web05.lansstyrelsen.se/transtat_O/transtat.asp>`_.

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

  >>> df = dataset.data.pandas  # get this dataset as a Pandas dataframe

Building a scraper
------------------
Scrapers are built by extending a base scraper, or a derative of that. You need to provide a method for listing datasets or collections of datasets, and for fetching data.

Statscraper is built for statistical data, meaning that it's most useful when the data you are scraping/fetching can be organized with a numerical value in each row:

========  ======  =======
  city     year    value
========  ======  =======
Voi       2009    45483
Kabarnet  2006    10191
Taveta    2009    67505
========  ======  =======

A scraper can override these methods:

* `_fetch_itemslist(item)` to yield collections or datasets at the current cursor position
* `_fetch_data(dataset)` to yield rows from the currently selected dataset
* `_fetch_dimensions(dataset)` to yield dimensions available for the currently selected dataset
* `_fetch_allowed_values(dimension)` to yield allowed values for a dimension

A number of hooks are avaiable for more advanced scrapers. These are called by adding the on decorator on a method:

.. code:: python

  @BaseScraper.on("up")
  def my_method(self):
    # Do something when the user moves up one level

For developers
==============
These instructions are for developers working on the BaseScraper. See above for instructions for developing a scraper using the BaseScraper.

Downloading
-----------

.. code:: bash

  git clone https://github.com/jplusplus/statscraper
  python setup.py install

This repo includes `statscraper-datatypes` as a subtree. To update this, do:

.. code:: bash

  git subtree pull --prefix statscraper/datatypes git@github.com:jplusplus/statscraper-datatypes.git master --squash


Tests
-----

Since 2.0.0 we are using pytest. To run an individual test:

.. code:: bash

  python3 -m pytest tests/test-datatypes.py


Changelog
---------
The changelog has been moved to `CHANGELOG.md <CHANGELOG.md>`_.

.. _Facebook: https://www.facebook.com/groups/skrejperpark
.. _ReadTheDocs: http://statscraper.readthedocs.io
