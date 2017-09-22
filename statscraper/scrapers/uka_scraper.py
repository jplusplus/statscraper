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
        """ Iterate through semesters, counties and municipalities.
        """
        yield Dimension(u"school")
        yield Dimension(u"year",
                        datatype="year")
        yield Dimension(u"semester",
                        datatype="academic_term",
                        dialect="swedish")  # HT/VT
        yield Dimension(u"municipality",
                        datatype="year",
                        domain="sweden/municipalities")

    def _fetch_data(self, dataset, query):
        url = "http://statistik.uka.se/4.5d85793915901d205f935d0f.12.5d85793915901d205f965eab.portlet?action=resultat&view=resultTable&frageTyp=3&frageNr=240&tid=%s&grupp1=%s&grupp2=%s"
        thenmap_url = "http://api.thenmap.net/v1/se-7/data/%s?data_props=name|kommunkod"
        # 6 is 1993, the first year in the db
        if query is None:
            query = {}
        if "from" not in query:
            query['from'] = 1993
        if "semesters" not in query:
            query['semesters'] = (2016 - query["from"]) * 2
        start = (query["from"] - 1993) * 2 + 5
        terms = range(start,
                      start + query["semesters"] + 2)
        for t in terms:
            # Get all municipalities, and their codes, from this year
            year = ((t - 5) / 2) + 1993
            semester = ["HT", "VT"][t % 2]
            municipalities = requests.get(thenmap_url % year).json()
            for id_, municipality_ in municipalities["data"].items():
                municipality = municipality_.pop()
                code = municipality["kommunkod"].zfill(4)
                c, m = code[:2], code[2:]
                html = requests.get(url % (t, c, m)).text
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find("table")
                # The first rows are headers, the last are empty
                rows = table.find_all("tr")[5:-2]
                for row in rows:
                    cells = row.find_all("td")

                    yield Result(cells[2].text.strip(), {
                        "municipality": municipality["name"],
                        "school": cells[0].text.strip(),
                        "semester": semester,
                        "year": year,
                    })
