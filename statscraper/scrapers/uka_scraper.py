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
            yield Dataset("municipality",
                          label="Students by municipality, school, semester.")

    def _fetch_dimensions(self, dataset):
        """ Declaring available dimensions like this is not mandatory,
         but nice, especially if they differ from dataset to dataset.

         If you are using a built in datatype, you can specify the dialect
         you are expecting, to have values normalized. This scraper will
         look for Swedish month names (e.g. 'Januari'), but return them
         according to the Statscraper standard ('january').
        """
        yield Dimension(u"school")
        yield Dimension(u"year",
                        datatype="year")
        yield Dimension(u"semester",
                        datatype="academic_term",
                        dialect="swedish")
        yield Dimension(u"municipality",
                        datatype="year",
                        domain="sweden/municipalities")

    def _fetch_data(self, dataset, query={'from': 1993,
                                          'semesters': 46}):
        url = "http://statistik.uka.se/4.5d85793915901d205f935d0f.12.5d85793915901d205f965eab.portlet?action=resultat&view=resultTable&frageTyp=3&frageNr=240&tid=%s&grupp1=%s&grupp2=%s"
        thenmap_url = "http://api.thenmap.net/v1/se-7/data/%s?data_props=name|kommunkod"
        # 6 is 1993, the first year in the db
        terms = range(query["from"] - 1987,
                      query["semesters"] + 7)
        for t in terms:
            # Get all municipalities, and their codes, from this year
            year = ((t - 5) / 2) + 1993
            semester = ["HT", "VT"][year % 2]
            municipalities = requests.get(thenmap_url % year).json()
            for id_, municipality_ in municipalities["data"].items():
                municipality = municipality_.pop()
                code = municipality["kommunkod"].zfill(4)
                c = code[:2]
                m = code[2:]
                html = requests.get(url % (t, c, m)).text
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find("table")

                rows = table.find_all("tr")[5:-2]
                for row in rows:
                    cells = row.find_all("td")

                    yield Result(cells[2].text.strip(), {
                        "municipality": municipality["name"],
                        "school": cells[0].text.strip(),
                        "semester": semester,
                        "year": year,
                    })
