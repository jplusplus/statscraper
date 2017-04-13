# Usage
This document outlines the proposed API for statscraper.

## Introduction
Statscraper provides a common set of guidelines, base classes and standards for writing scrapers for Swedish agencies' websites. Each scraper is developed independently.

## API

### Exploring sites
Some sites are simple, with a basic list of datasets as its only pre-dataset layer.

```python
import AMS

scraper = AMS()
scraper.list()
# [<Dataset: 'unemployment'>, <Dataset: 'youth-unemployment'>]
```

Others are more complex, consisting of multiple navigation layers. The scraper provides a cursor-like object for navigating the data.

```python
import SCB

scraper = SCB()
scraper.list()
# [<Topic: 'Labor market'>, <Topic: 'Population'> ...]
topic = scraper.get('Labor market')
topic.list()
# [<Topic: 'AKU'>, <Topic: 'Labour cost index'> ...]

# Alternatively:
scraper.get('Labor market').get('AKU')
```

The primary methods of navigating a site is `list` and `get`. The former lists all available topics or data sets at the current level, whereas the latter selects a level and/or dataset.


### Exploring data sets
Some data sets represents search interfaces, whereas others are simply tables without configuration settings.

```python
unemployment = scraper.topic('unemployment')
unemployment.label
# u"Arbetslöshet"

unemployment.dimensions
# ['gender', 'municipality', 'period']

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
```

Simple data sets are fetched using:

```python
resultset = unemployment.get()
```

Queryable data sets take parameters:

```python
resultset = unemployment.get({
    'municipality': 'Huddinge kommun',
    'period': '2016-12', 
})
```

### Exploring the actual data
Resultsets have a `describe` method which provides some basic information about the data.

```python
resultset.describe()
# Length:     123456
# Dimensions: ['gender', 'municipality', 'period']
# Measures:   ['count', 'rate', 'change']
# ...

resultset.length
# 123456

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

### Exporting data

resultset.to_dataframe()
resultset.to_dictlist()

resultset.to_csv('my_data.csv')
resultset.to_xlsx('my_data.xlsx')
resultset.to_json('my_data.json')
resultset.to_jsonstat('my_jsonstat.json')
```
