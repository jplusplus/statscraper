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
        # TODO: Should probably wait for a specific
        # element to appear on the site
        self.browser.implicitly_wait(5)

    @BaseScraper.on("select")
    def switch_dataset(self, id_):

        # `id_` is equal to `self.current_item.id`
        # `id_` can be either "Arbetsolycka" or "Arbetssjukdom"
        xpath = "//div[@title='%s']" % id_
        button = self.browser.find_element_by_xpath(xpath)
        button.click()

    def _fetch_itemslist(self, item):
        """ This data can be parsed in different ways,
        but we chose to define two datasets: Number of work injuries,
        and number of workrelated diseases.
        """
        assert item.is_root
        yield Dataset("Arbetsolycka")
        yield Dataset("Arbetssjukdom")

    def _fetch_data(self, dataset, query=None):
        yield Result(37, {"test": "test"})
