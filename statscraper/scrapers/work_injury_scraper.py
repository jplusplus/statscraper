# encoding: utf-8
""" A scraper to fetch Swedish work injury stats from
    http://webbstat.av.se

    This is an example of a scraper using Selenium.
    TODO: Move some useful functionality to a SeleciumFirefoxScraper
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from statscraper import BaseScraper, Collection, Dataset, Result
import os
from glob import iglob
from uuid import uuid4
from openpyxl import load_workbook
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

DEFAULT_TEMPDIR = "./tmp"
TEMPDIR_ENVVAR = "STATSCRAPER_TEMPDIR"
PAGELOAD_TIMEOUT = 90  # seconds


class WorkInjuries(BaseScraper):

    tempdir = "./tmp"

    @BaseScraper.on("init")
    def initiate_browser(self):

        # Create a unique tempdir for downloaded files
        tempdir = os.getenv(TEMPDIR_ENVVAR, DEFAULT_TEMPDIR)
        tempsubdir = uuid4().hex
        # TODO: Remove this directory when finished!
        self.tempdir = os.path.join(tempdir, tempsubdir)
        try:
            # Try and create directory before checking if it exists,
            # to avoid race condition
            os.makedirs(self.tempdir)
        except OSError:
            if not os.path.isdir(self.tempdir):
                raise

        profile = webdriver.FirefoxProfile()
        # Set download location, avoid download dialogues if possible
        # Different settings needed for different Firefox versions
        # This will be a long list...
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.manager.closeWhenDone', True)
        profile.set_preference('browser.download.dir', self.tempdir)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream;application/vnd.ms-excel")
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("browser.download.manager.useWindow", False)

        self.browser = webdriver.Firefox(profile)

        self.browser.get('http://webbstat.av.se')
        # Wait for a content element, and 3 extra seconds just in case
        WebDriverWait(self.browser, PAGELOAD_TIMEOUT)\
            .until(EC.presence_of_element_located((By.ID, '41')))
        self.browser.implicitly_wait(3)

        detailed_cls = "Document_TX_GOTOTAB_Avancerad"
        self.browser\
            .find_element_by_class_name(detailed_cls)\
            .find_element_by_tag_name("td")\
            .click()
        # Wait for a content element, and 3 extra seconds just in case
        WebDriverWait(self.browser, PAGELOAD_TIMEOUT)\
            .until(EC.presence_of_element_located((By.ID, '41')))
        self.browser.implicitly_wait(3)

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
        # Press enter twice in case of any prompts
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.RETURN)
        actions.send_keys(Keys.RETURN)
        actions.perform()

        # WARNING: Assuming the latest download to be our file.
        # This is obviously not 100 % water proof.
        latest_download = min(iglob(self.tempdir), key=os.path.getctime)
        workbook = load_workbook(latest_download)
        sheet = workbook.active
        print latest_download
        for rownum in xrange(sheet.nrows):
            print sheet.row_values(rownum)
        exit()
        # TODO: Open and parse Excelfile
        # The Excel-file should now be in the default temp dir of the system
        yield Result(37, {"test": "test"})
