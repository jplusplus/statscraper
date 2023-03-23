- 2.0.2

  - remove debug prints from SMHI scraper
  - upgrade BeautifulSoup to work with Pyhon 3.10+

- 2.0.1

  - Use https endpoint in SCB Scraper.

- 2.0.0

  - Python 2 support deprecated. We will slowly phase out support.
  - Fix a bug with `DimensionValue.translate()` in Python 3.
  - Make `translate()` raise errors when it couldn't translate.
  - The municipality of Gotland is now known as 'Region Gotland' (was: Gotlands kommun).
  - Added some useful built-in filters to the SCB-scraper, to get results by eg municipality.
  - Upstream fix for typo in datatype region:sweden/municipality Vännäs kommun
  - SCB scraper will raises exception when an error message is returned
  - Fixes Python3 bug in SMHI scraper

- 1.0.7

  - Bara kommun added to Swedish municipalities
  - Remove logic from SCBScraper that is already handled by BaseScraper

- 1.0.6

  - Added dialect:skatteverket (two/four digit county/municipality codes)
  - Added data type for road category
  - Make SCB scraper treat a “Region” as, well, a region

- 1.0.5
  - Added station key to SMHI scraper

- 1.0.4
  - Added SMHI scraper

- 1.0.3
  - Re-add demo scrapers that accidentally got left out in the first release

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
