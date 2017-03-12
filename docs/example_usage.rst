Example usage
-------------

Exploring sites
~~~~~~~~~~~~~~~
Some sites are simple, with a basic list of datasets as its only pre-dataset layer.

.. code:: python

    import AMS

    scraper = AMS()
    scraper.list()
    # [<Dataset: 'unemployment'>, <Dataset: 'youth-unemployment'>]

Others are more complex, consisting of multiple navigation layers. The scraper provides a cursor-like object for navigating the data.

.. code:: python

    import SCB

    scraper = SCB()
    scraper.list()
    # [<Topic: 'Labor market'>, <Topic: 'Population'> ...]
    topic = scraper.get('Labor market')
    topic.list()
    # [<Topic: 'AKU'>, <Topic: 'Labour cost index'> ...]

    # Alternatively:
    scraper.get('Labor market').get('AKU')

The primary methods of navigating a site is `list` and `get`. The former lists all available topics or data sets at the current level, whereas the latter selects a level and/or dataset.


Exploring data sets
~~~~~~~~~~~~~~~~~~~

Some data sets represents search interfaces, whereas others are simply tables without configuration settings.

.. code:: python

    # Get by id
    unemployment = scraper.topic('unemployment')
    unemployment.label
    # u"Arbetslöshet"

    # Get by label
    unemployment = scraper.topic(u"Arbetslöshet")
    unemployment.label
    # u"Arbetslöshet"


    unemployment.dimensions
    # [<Dimension: 'gender'>, <Dimension: 'municipality'>, <Dimension: 'period'>]

    gender = unemployment.dimension("gender")
    gender.allowed_values
    # ["all", "male", "female"]
    gender.default
    # "all"
    gender.label
    # "Kön"

    men = gender.category("male")
    men.label
    # u"Män"

    unemployment.id
    # u"male"

Simple data sets are fetched using:

.. code:: python

    resultset = unemployment.get()

Queryable data sets take parameters:

.. code:: python

    resultset = unemployment.get({
        'municipality': 'Huddinge kommun',
        'period': '2016-12', 
    })

    resultset = unemployment.get({
        'municipality': ['Stockholms kommun', 'Solna kommun' ],
        'period': ['2016-01', 2016-02, 2016-03'], 
    })

When querying a dataset you should not have to worry about the naming convention of the given site. You can used a standarized one defined in our ontlogy, or one that you are comfortable with. 

.. code:: python

    # Make a query with the standarized ontology 
    resultset = unemployment.get({
        'municipality': ['Stockholms kommun' ],
    }, dialect="default")

    # ...or a specific one
    resultset = unemployment.get({
        'municipality': ['Stockholm' ],
    }, dialect="Kolada")




Exploring the actual data
~~~~~~~~~~~~~~~~~~~~~~~~~

Resultsets have a `describe` method which provides some basic information about the data.

.. code:: python

    resultset.describe()
    # Length:     123456
    # Dimensions: ['gender', 'municipality', 'period']
    # Measures:   ['count', 'rate', 'change']
    # ...

    resultset.length
    # 123456


You can explore a resultset with the same methods that you explore a dataset (eg`.dimensions`, `.dimension("reigon")` etc.) 

.. code:: python

    resultset.dimensions
    # ['gender', 'municipality', 'period']

    regions = resultset.dimension("municipality")
    regions.categories
    # ['Huddinge kommun']

    regions.note
    # u'Hebys gränser förändrades 2007'

    huddinge = regions.category("Huddinge kommun")
    huddinge.id
    # 'Huddinge kommun'
    huddinge.label
    # 'Huddinge kommun'

    resultset.measures
    # ['count', 'rate', 'change']

    count = resultset.measure('count')
    count.label
    # 'Antal öppet arbetslösa'

Exporting data
~~~~~~~~~~~~~~

A resultset can be exported to a number of formats.

.. code:: python

    resultset.to_dataframe()
    resultset.to_dictlist()

    resultset.to_csv('my_data.csv')
    resultset.to_xlsx('my_data.xlsx')
    resultset.to_jsonstat('my_jsonstat.json')

The resultset can be converted to either id's or labels.


    # Export with id's as content
    resultset.to_dataframe(content="index")

    # Export with labels as content
    resultset.to_dataframe(content="label")

Or translated to a specfic dialect using our ontology.

.. code:: python
    resultset.to_dataframe(dialect="default")    
    resultset.to_dataframe(dialect="SCB")    
    resultset.to_dataframe(dialect="Kolada")    



