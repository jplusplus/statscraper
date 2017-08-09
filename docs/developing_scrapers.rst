===================
Developing scrapers
===================
The scraper can navigate though an hierarchy of collections and datasets. Collections and datasets are refered to as “items”.

:: 

        ┏━ Collection ━━━ Collection ━┳━ Dataset
  ROOT ━╋━ Collection ━┳━ Dataset     ┣━ Dataset
        ┗━ Collection  ┣━ Dataset     ┗━ Dataset
                       ┗━ Dataset

  ╰─────────────────────────┬───────────────────────╯
                       items

 Scrapers are built by extending the BaseScraper class, or a subclass of it. Every scraper must override the methods :code:`_fetch_itemslist` and :code:`_fetch_data`:

  * :code:`_fetch_itemslist(self, item)` must yield items at the current position.
  * :code:`_fetch_data(self, dataset, query)` must yield rows from a dataset.

 Other methods that a scraper can chose to override are:

  * :code:`_fetch_dimensions(dataset)` should yield dimensions available on a dataset.
  * :code:`_fetch_allowed_values(self, dimension)` should yield allowed values for a dimension.

 A number of hooks are avaiable for more advanced scrapers. These are called by adding the on decorator on a method:

.. code:: python

    @BaseScraper.on("up")
    def my_method(self):
      # Do something when the cusor moves up one level

Check out the `statscraper/scrapers <https://github.com/jplusplus/statscraper/tree/master/statscraper/scrapers>`_ directory for some scraper examples.
