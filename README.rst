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

Here's a simple example, with a scraper that returns only a single dataset:

.. code:: python

  # encoding: utf-8
  """ Get the number of cranes at Hornborgarsjön """
  from statscraper.scrapers import Cranes

  scraper = Cranes()
  print scraper.items  # List available datasets
  # [<Dataset: Number of cranes>]

  dataset = scraper.items[0]
  print dataset.dimensions
  # [<Dimension: date (date)>, <Dimension: month (month)>, <Dimension: year (year)>]

  print dataset.data[0]  # Print first row of data
  # {'date': u'1', 'year': u'2010', 'value': u'', 'month': u'januari'}

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

  @on("up")
  def my_method(self):
    # Do something when the user moves up one level

Available hooks are:

* `init`: Called when initiating the BaseScraper
* `up`: Called when trying to go up one level
* `select`: Called when trying to move to a Collection or Dataset
* `top`: Called when reaching the top level


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

- 1.0.0.dev1
  - Semantic versioning starts here
  - Implement datatypes and dialects

- 0.0.2
    
  - Added some demo scrapers
  - The cursor is now moved when accessing datasets
  - Renamed methods for moving cursor: move_up(), move_to()
  - Added many more methods
  - Added tests
  - Added datatypes subtree
  - It should now be possible to write a basic scraper

- 0.0.1
    
  - First version

.. _Facebook: https://www.facebook.com/groups/skrejperpark
.. _ReadTheDocs: http://statscraper.readthedocs.io
