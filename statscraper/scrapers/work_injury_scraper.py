# encoding: utf-8
""" A scraper to fetch Swedish work injury stats from
    http://webbstat.av.se

    This is an example of a scraper using Selenium.
    TODO: Move some useful functionality to a SeleciumFirefoxScraper

    To change download location:
       export STATSCRAPER_TEMPDIR="/path/to/temp/dir"

"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from statscraper import BaseScraper, Collection, Dataset, Result, Dimension
import os
from glob import iglob
from time import sleep
from uuid import uuid4
from xlrd import open_workbook
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
        detailed_cls = "Document_TX_GOTOTAB_Avancerad"
        """ The button for expanded detailed options. This
        also happens to be a good indicator as to wheter
        all content is loaded.
        """

        # Wait for a content element, and 3 extra seconds just in case
        WebDriverWait(self.browser, PAGELOAD_TIMEOUT)\
            .until(EC.presence_of_element_located((By.CLASS_NAME,
                                                  detailed_cls)))
        self.browser.implicitly_wait(3)

        self.browser\
            .find_element_by_class_name(detailed_cls)\
            .find_element_by_tag_name("td")\
            .click()
        # Wait for a content element, and 3 extra seconds just in case
        WebDriverWait(self.browser, PAGELOAD_TIMEOUT)\
            .until(EC.presence_of_element_located((By.CLASS_NAME,
                                                   detailed_cls)))
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
        period = "Månad" if p == u"månad" else "År och månad"
        xpath = "//div[@class='QvListbox']//div[@title='%s']" % period
        self.browser\
            .find_element_by_xpath(xpath)\
            .click()

    def _fetch_dimensions(self, dataset):
        """ Declaring available dimensions like this is not mandatory,
         but nice, especially if they differ from dataset to dataset.

         If you are using a built in datatype, you can specify the dialect
         you are expecting, to have values normalized. This scraper will
         look for Swedish month names (e.g. 'Januari'), but return them
         according to the Statscraper standard ('january').
        """
        yield Dimension(u"region",
                        label="municipality or county",
                        datatype="region",
                        dialect="arbetsmiljoverket")
        yield Dimension(u"period",
                        label="Year or month")

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
            for r in [u"kommun", u"län"]:
                for p in [u"år", u"månad"]:
                    yield Dataset(u"%s-%s-%s" % (c, r, p),
                                  blob=(c, r, p),
                                  label=u"%s, antal per %s och %s" % (c, r, p))

    def _fetch_data(self, dataset, query=None):
        (c, r, p) = dataset.blob

        self.browser\
            .find_element_by_xpath("//div[@title='Skicka till Excel']")\
            .click()
        # Press enter trice in case of any prompts
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.RETURN)
        actions.send_keys(Keys.RETURN)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        # Wait for download
        i = 0
        while not os.listdir(self.tempdir):
            sleep(1)
            i += 1
            if i > PAGELOAD_TIMEOUT:
                # TODO: Use a suitable basescraper exception
                raise Exception("Download timed out")
        sleep(20)  # TODO: We need to check that the file is complete.
        # Something like this:
        # https://stackoverflow.com/questions/35891393/how-to-get-file-download-complete-status-using-selenium-web-driver-c-sharp#35892347

        # WARNING: Assuming the latest downloaded xls to be our file.
        # This is obviously not 100 % water proof.
        latest_download = max(iglob(os.path.join(self.tempdir, "*.xls")),
                              key=os.path.getctime)
        workbook = open_workbook(latest_download)
        sheet = workbook.sheet_by_index(0)
        periods = sheet.row_values(0)[2:-1]
        periods = [int(x) for x in periods]
        for n in range(1, sheet.nrows):
            row = sheet.row_values(n)
            region = row.pop(0)
            row.pop(0)  # empty due to merged cells
            if region == "Total":
                break
            i = 0
            for col in row[:-1]:
                yield Result(
                    int(col),
                    {
                        "region": region,
                        "period": periods[i],
                    }
                )
