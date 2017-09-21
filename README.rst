Statscraper is a base library for building web scrapers for statistical data, with a helper ontology for (primarily Swedish) statistical data. A set of ready-to-use scrapers are included.

For users
=========

You can use Statscraper as a foundation for your next scraper, or try out any of the included scrapers. With Statscraper comes a unified interface for scraping, and some useful helper methods for scraper authors.

Full documentation: ReadTheDocs_

For updates and discussion: Facebook_

By `Journalism++ Stockholm <http://jplusplus.se>`_, and Robin Linderborg.

Installing
----------

.. code:: bash

  pip install statscraper

Using a scraper
---------------
Scrapers acts like “cursors” that move around a hierarchy of datasets and collections of dataset. Collections and datasets are refered to as “items”.

:: 

        ┏━ Collection ━━━ Collection ━┳━ Dataset
  ROOT ━╋━ Collection ━┳━ Dataset     ┣━ Dataset
        ┗━ Collection  ┣━ Dataset     ┗━ Dataset
                       ┗━ Dataset

  ╰─────────────────────────┬───────────────────────╯
                       items

Here's a simple example, with a scraper that returns only a single dataset: The number of cranes spotted at Hornborgarsjön each day as scraped from `Länsstyrelsen Östergötland <http://web05.lansstyrelsen.se/transtat_O/transtat.asp>`_.

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

  git clone https://github.com/jplusplus/skrejperpark
  python setup.py install

Tests
-----

.. code:: bash

  python setup.py test

Run `python setup.py test` from the root directory. This will install everything needed for testing, before running tests with `nosetests`.


Changelog
---------

- 1.0.3
  - Re-add demo scrapers that accidently got left out in the first release

- 1.0.0
  - First release

- 1.0.0.dev2
  - Implement translation
  - Add Dataset.fetch_next() as generator for results

- 1.0.0.dev1
  - Semantic versioning starts here
  - Implement datatypes and dialects

- 0.0.2
    
  - Added some demo scrapers
  - The cursor is now moved when accessing datasets
  - Renamed methods for moving cursor: move_up(), move_to()
  - Added tests
  - Added datatypes subtree

- 0.0.1
    
  - First version

.. _Facebook: https://www.facebook.com/groups/skrejperpark
.. _ReadTheDocs: http://statscraper.readthedocs.io
