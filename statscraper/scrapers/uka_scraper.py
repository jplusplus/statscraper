# encoding: utf-8
u""" A scraper to fetch Swedish university application statistics from
 the Swedish Higher Education Authority (Universitetskanslerämbetet, UKÄ),
 at http://statistik.uka.se
"""
from statscraper import BaseScraper, Dataset, Dimension, Result, Collection
import requests
from bs4 import BeautifulSoup


class UKA(BaseScraper):

    def _fetch_itemslist(self, item):
        """ We only offer regional application stats.
         Other collections are differently structured.
        """
        if item.is_root:
            yield Collection("regional",
                             label="New students by area and school.")
        else:
            yield Dataset("county",
                          label="New students by county, school and semester.")

    def _fetch_dimensions(self, dataset):
        """ Declaring available dimensions like this is not mandatory,
         but nice, especially if they differ from dataset to dataset.

         If you are using a built in datatype, you can specify the dialect
         you are expecting, to have values normalized. This scraper will
         look for Swedish month names (e.g. 'Januari'), but return them
         according to the Statscraper standard ('january').
        """
        yield Dimension(u"school")
        yield Dimension(u"semester")
        yield Dimension(u"year", datatype="year")
        yield Dimension(u"semester",
                        datatype="academic_term",
                        dialect="swedish")

    def _fetch_data(self, dataset, query=None):
        url = "http://statistik.uka.se/4.5d85793915901d205f935d0f.12.5d85793915901d205f965eab.portlet?action=resultat&view=resultTable&frageTyp=3&frageNr=240&tid=%s&grupp1=%s&grupp2=%s"
        terms = [6]
        counties = [{
            'id': "10",
            'municipalities': ["80"]
        }, ]
        for t in terms:
            for c in counties:
                for m in c["municipalities"]:
                    html = requests.get(url % (t, c, m["id"])).text
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find("table")
                    row = table.find_all("tr")[5:]
                    cells = row.find_all("td")
                    print cells[0].text,
                    print cells[2].text
                    """
                    yield Result(value.text.encode("utf-8"), {
                        "date": date,
                        "month": month,
                        "year": years[i],
                    })
                    """
