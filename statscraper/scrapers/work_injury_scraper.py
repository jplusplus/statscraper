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
        xpath = "//div[@title='%s']" % id_
        # `id_` can be either "Arbetsolycka" or "Arbetssjukdom"
        button = self.browser.find_element_by_xpath(xpath)
        button.click()

    def _fetch_itemslist(self, item):
        """ We define two datasets:
        - Number of work injuries ("Arbetsolycka")
        - Number of workrelated diseases ("Arbetssjukdom")
        """
        yield Dataset("Arbetsolycka")
        yield Dataset("Arbetssjukdom")

    def _fetch_data(self, dataset, query=None):
        yield Result(37, {"test": "test"})
