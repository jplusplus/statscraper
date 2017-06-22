==============
Using dialects
==============

.. NOTE::

   This documentation refers to version 0.0.1. As of 0.0.2, the interface has changed considerably.

`statscraper.dialect` is a library for harmonizing namings of regions and common dimensions across different statistical datasources.

Basic usage
-----------

.. code:: python

    import dialects

    dialect = dialects("SCB")

    # A dialect consists of a number of domains
    dialect.domains
    # [ "<Domain: region/county>", "<Domain: region/municipality>" ]
    

    # You must specify under which domain(s) to get a certain entity
    domain = dialect.domain("region/municipality")
    stockholm = domain(u"Stockholms kommun")
    
    # Every entity as an id
    stockholm.id
    # "0180"

    # ... and a label
    stockholm.label()
	# "Stockholms kommun" 
	
	# ...potentially also in other languages
	stockholm.label(lang="en")
	# "Stockholm municipality"

	# Use .to() to translate to another dialect
	stockholm.to("Kolada").id
	# "Stockholm"

	stockholm.to("Kolada").label
	# "Stockholm"

Usage with statscraper
----------------------

If a `statscraper` is properly configured with a dialect you can easily translate a resultset to any other dialect.

.. code:: python

	resultset.to_dataframe(dialect='Kolada')  
	resultset.to_dataframe(dialect='SCB', lang="en")    
