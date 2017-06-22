==============
Using scrapers
==============

.. NOTE::

   This documentation refers to version 0.0.1. As of 0.0.2, the interface has changed considerably.


Exploring sites
---------------
The primary methods of navigating a site is `list` and `get`. The former lists all available topics or data sets at the current level, whereas the latter selects a level or a dataset.

Some sites are simple, consisting of a basic list of datasets.

.. code::

    >>> import AMS

    >>> scraper = AMS()
    >>> scraper.list()
    [<Dataset: 'unemployment'>, <Dataset: 'youth-unemployment'>]

Others have a more complex hierarchical layout. The scraper provides a cursor-like functionality for navigating the site.

.. code::

    >>> import SCB

    >>> scraper = SCB()
    >>> scraper.list()
    [<Topic: 'Labor market'>, <Topic: 'Population'>]

    >>> topic = scraper.get('Labor market')
    >>> topic.list()
    [<Topic: 'AKU'>, <Topic: 'Labour cost index'> ...]

Alternatively, chain the method calls:

    >>> scraper.get('Labor market').get('AKU')


Exploring data sets
-------------------

Once a data set is selected, the actual data is downloaded using the `fetch` method. This returns a `resultset`.

    >>> unemployment = scraper.get('unemployment')
    >>> unemployment.fetch()
    <Resultset: 'unemployment'>

Some data sets represents search interfaces, whereas others are simply tables without configuration settings. Queryable data sets take parameters:

.. code:: python

    >>> resultset = unemployment.fetch({
    ...     'municipality': 'Huddinge kommun',
    ...     'period': '2016-12', 
    ... })

    >>> resultset = unemployment.fetch({
    ...    'municipality': ['Stockholms kommun', 'Solna kommun' ],
    ...    'period': ['2016-01', '2016-02', '2016-03'], 
    ... })

When querying a data set you should not have to worry about the naming convention of the given site. You can use a standarized one defined in our ontology, or one that you are comfortable with. 

Make a query with the standarized ontology:
 
    >>> resultset = unemployment.get({
    ...    'municipality': ['Stockholms kommun' ],
    ... }, dialect="default")

Or a specific one:

    >>> resultset = unemployment.get({
    ...     'municipality': ['Stockholm' ],
    ... }, dialect="Kolada")

TODO: Describe these snippets.

Get by id

    >>> unemployment = scraper.get('unemployment')
    >>> unemployment.label
    u'Arbetslöshet'

Get by label

    >>> unemployment = scraper.get(u'Arbetslöshet')
    >>> unemployment.label
    u'Arbetslöshet'

    >>> unemployment.dimensions
    [<Dimension: 'gender'>, <Dimension: 'municipality'>, <Dimension: 'period'>]

    >>> gender = unemployment.dimension('gender')
    >>> gender.allowed_values
    ['all', 'male', 'female']
    
    >>> gender.default
    'all'
    
    >>> gender.label
    'Kön'

    >>> men = gender.category('male')
    >>> men.label
    u'Män'

    >>> unemployment.id
    u'male'


Exploring the actual data
-------------------------

Resultsets have a `describe` method which provides some basic information about the data. These properties are also available as attributes of the resultset.

.. code:: python

    >>> resultset.describe()
    {
        'shape': (8350, 14),
        'dimensions': ['gender', 'municipality', 'period', 'measure']
    }

    >>> resultset.shape
    (8350, 14)


You can explore a resultset with the same methods that you explore a dataset (eg `.dimensions`, `.dimension("region")` etc.) 

.. code:: python

    >>> resultset.dimensions
    ['gender', 'municipality', 'period']

    >>> regions = resultset.dimension("municipality")
    >>> regions.categories
    ['Huddinge kommun']

    >>> regions.note
    u'Hebys gränser förändrades 2007'

    >>> huddinge = regions.category("Huddinge kommun")
    >>> huddinge.id
    'Huddinge kommun'
    
    >>> huddinge.label
    'Huddinge kommun'


Exporting data
--------------

A resultset can be exported to a number of formats.

.. code:: python

    resultset.to_dataframe()
    resultset.to_dictlist()

    resultset.to_csv('my_data.csv')
    resultset.to_xlsx('my_data.xlsx')
    resultset.to_jsonstat('my_jsonstat.json')

The resultset can be converted to either id's or labels.

.. code:: python
    
    # Export with id's as content
    resultset.to_dataframe(content='index')

    # Export with labels as content
    resultset.to_dataframe(content='label')

Or translated to a specfic dialect using our ontology.

.. code:: python

    resultset.to_dataframe(dialect='default')    
    resultset.to_dataframe(dialect='SCB')    
    resultset.to_dataframe(dialect='Kolada')    



