# encoding: utf-8
""" A scraper to fetch Swedish work injury stats from
    http://webbstat.av.se

    This is an example of a scraper using Selenium.
"""
from selenium import webdriver
from statscraper import BaseScraper, Collection, Dataset, Result
from tempfile import gettempdir


class WorkInjuries(BaseScraper):

    @BaseScraper.on("init")
    def initiate_browser(self):

        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)  # custom download location
        profile.set_preference('browser.download.manager.showWhenStarting', False)  # No download dialogue
        profile.set_preference('browser.download.dir', gettempdir())

        self.browser = webdriver.Firefox(profile)
        self.browser.get('http://webbstat.av.se')
        # Selenium has trouble understanding when this page is loaded,
        # so wait for 5 extra seconds, just in case
        self.browser.implicitly_wait(5)
        detailed_cls = "Document_TX_GOTOTAB_Avancerad"
        self.browser\
            .find_element_by_class_name(detailed_cls)\
            .find_element_by_tag_name("td")\
            .click()
        self.browser.implicitly_wait(5)

    @BaseScraper.on("select")
    def switch_dataset(self, id_):
        (c, r, p) = self.current_item.blob

        # Select collection
        xpath = "//div[@title='%s']" % c
        # `c` can be either "Arbetsolycka" or "Arbetssjukdom"
        button = self.browser.find_element_by_xpath(xpath)
        button.click()

        # select Kommun or Län
        xpath = '//div[@class="QvContent"]/div[@class="QvGrid"]//div[@title="Visa tabell per:"]'
        self.browser\
            .find_element_by_xpath(xpath)\
            .click()
        region = "Kommun" if r == "kommun" else "Län"
        xpath = "//div[@class='QvListbox']//div[@title='%s']" % region
        self.browser\
            .find_element_by_xpath(xpath)\
            .click()

        # select Månad or År
        xpath = '//div[@class="QvContent"]/div[@class="QvGrid"]//div[@title="Tidsenhet:"]'
        self.browser\
            .find_element_by_xpath(xpath)\
            .click()
        period = "Månad" if p == "månad" else "År och månad"
        xpath = "//div[@class='QvListbox']//div[@title='%s']" % period
        self.browser\
            .find_element_by_xpath(xpath)\
            .click()

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
                yield Collection(c, blob=(c, None, None))
        else:
            c = item.id
            for r in ["kommun", "län"]:
                for p in ["år", "månad"]:
                    yield Dataset("%s-%s-%s" % (c, r, p),
                                  blob=(c, r, p),
                                  label="%s, antal per %s och %s" % (c, r, p))

    def _fetch_data(self, dataset, query=None):
        (c, r, p) = dataset.blob

        self.browser\
            .find_element_by_xpath("//div[@title='Skicka till Excel']")\
            .click()
        # TODO: Download and parse Excelfile
        yield Result(37, {"test": "test"})
