# encoding: utf-8
""" A scraper to fetch Swedish work injury stats from
    http://webbstat.av.se

    This is an example of a scraper using Selenium.
"""
from selenium import webdriver
from statscraper import BaseScraper, Dataset, Result


class WorkInjuries(BaseScraper):

    @BaseScraper.on("init")
    def initiate_browser(self):
        self.browser = webdriver.Firefox()
        self.browser.get('http://webbstat.av.se')
        # Selenium has trouble understanding when this page is loaded,
        # so wait for 5 extra seconds, just in case
        self.browser.implicitly_wait(5)

    @BaseScraper.on("select")
    def switch_dataset(self, id_):
        (c, r, p) = self.current_item.blob

        # Select collection
        xpath = "//div[@title='%s']" % c
        # `c` can be either "Arbetsolycka" or "Arbetssjukdom"
        button = self.browser.find_element_by_xpath(xpath)
        button.click()

        # Select region
        # Select period

    def _fetch_itemslist(self, item):
        """ We define two collection:
        - Number of work injuries ("Arbetsolycka")
        - Number of workrelated diseases ("Arbetssjukdom")
        Each contains four datasets:
        - Per municipality and year
        - Per county and year
        - Per municipality and month
        - Per municipality and year
        """
        if item.is_root:
            for c in ["Arbetsolycka", "Arbetssjukdom"]:
                yield Dataset(c, blob=(c, None, None))
        else:
            c = item.id
            for r in ["kommun", "län"]:
                for p in ["år", "månad"]:
                    yield Dataset("%s-%s-%s" % (c, r, p),
                                  blob=(c, r, p),
                                  label="%s, antal per %s och %s" % (c, r, p))

    def _fetch_data(self, dataset, query=None):
        yield Result(37, {"test": "test"})
