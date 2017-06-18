# Statscraper Datatypes
This repo contains data types (e.g. ”Swedish municipality”), with value types (e.g. ”string”), allowed values, names lookup tables for alternative names, and definitions. It is used by the Statscraper repo, as a semi standardized ontology for scrapers.

All datatypes are listed in `/datatypes.csv`. Allowed values are in the `/values` folder, organized in further subfolders by domain.

## Data types (datatypes.csv)
`datatypes.csv` contains for each datatype:
 - `id`: A unique id. We use human readable id's.
 - `description`: Should include a definition
 - `value_type`: `int`, `float`, `str`, `date` or `bool`
 - `allowed_values`: See below

### Value types
Each data type can have one of the following value types:

* `int` – a value that can be parsed as an integer 
* `float` – a value that can be parsed as a floating-point number
* `str` – a value that can be parsed as a string. Empty strings are considered null.
* `date` – a ISO 8601 date, e.g. `2016-07-05`, `2016-07-05T13:00:00`, `2016-W27`, or `1981-04`.
* `bool` – 1 for True and 0 False. Blank means null.

## Allowed values

Some data types, and some metadata fields, have a predefined set of allowed values (such as “regions”). In some domains, allowed values may be organized in categories (such as “Swedish municipalities”, “Swedish counties”).

Allowed values are specified in csv files under the `values` directory, optionlly structured in subfolders by domain, e.g.`regions/sweden/municipalities.csv`. They are referenced like this: `regions/sweden/municipalities`, and `regions`. If there is a `regions/` folder, there can not be a `regions.csv` in the same directory.

The allowed values csv's contain:

* `id`: A unique id. We use human readable id's, e.g. "Stockholms kommun", not "0180"
* `label`: An optional label
* `dialect:`~: Columns prefixed with `dialect:` contain corresponding id's, e.g. names useed by major statistical providers, WikiData id's, etc
