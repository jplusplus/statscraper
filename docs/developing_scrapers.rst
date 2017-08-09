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

  * :code:`_fetch_dimensions(self, dataset)` should yield dimensions available on a dataset.
  * :code:`_fetch_allowed_values(self, dimension)` should yield allowed values for a dimension.

A number of hooks are avaiable for more advanced scrapers. These are called by adding the on decorator on a method:

.. code:: python

    @BaseScraper.on("up")
    def my_method(self):
      # Do something when the cusor moves up one level

Check out the `statscraper/scrapers <https://github.com/jplusplus/statscraper/tree/master/statscraper/scrapers>`_ directory for some scraper examples.

Below if the full code for the CranesScraper scraper used in the chapter `Using Scrapers <//statscraper.readthedocs.io/en/latest/using_scrapers.html>`_:

.. code:: python

    # encoding: utf-8
    """ A scraper to fetch daily cranes sightings at Hornborgasjön
        from http://web05.lansstyrelsen.se/transtat_O/transtat.asp
        This is intended to be a minimal example of a scraper
        using Beautiful Soup.
    """
    import requests
    from bs4 import BeautifulSoup
    from statscraper import BaseScraper, Dataset, Dimension, Result


    class Cranes(BaseScraper):

        def _fetch_itemslist(self, item):
            """ There is only one dataset. """
            yield Dataset("Number of cranes")

        def _fetch_dimensions(self, dataset):
            """ Declaring available dimensions like this is not mandatory,
             but nice, especially if they differ from dataset to dataset.

             If you are using a built in datatype, you can specify the dialect
             you are expecting, to have values normalized. This scraper will
             look for Swedish month names (e.g. 'Januari'), but return them
             according to the Statscraper standard ('january').
            """
            yield Dimension(u"date", label="Day of the month")
            yield Dimension(u"month", datatype="month", dialect="swedish")
            yield Dimension(u"year", datatype="year")

        def _fetch_data(self, dataset, query=None):
            html = requests.get("http://web05.lansstyrelsen.se/transtat_O/transtat.asp").text
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find("table", "line").find_all("table")[2].findNext("table")
            rows = table.find_all("tr")
            column_headers = rows.pop(0).find_all("td", recursive=False)
            years = [x.text for x in column_headers[2:]]
            for row in rows:
                cells = row.find_all("td")
                date = cells.pop(0).text
                month = cells.pop(0).text
                i = 0
                for value in cells:
                    # Each column from here is a year.
                    if value.text:
                        yield Result(value.text.encode("utf-8"), {
                            "date": date,
                            "month": month,
                            "year": years[i],
                        })
                    i += 1
