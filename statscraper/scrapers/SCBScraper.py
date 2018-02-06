# encoding: utf-8
""" A wrapper around the SCB API, demonstrating how to extend
    a scraper in the scraper park.
"""
from .PXWebScraper import PXWeb, Dimension


class SCB(PXWeb):

    base_url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd'

    def _fetch_dimensions(self, dataset):
        """
            We override this method just to set the correct datatype
            and dialect for regions.
        """
        for dimension in super(SCB, self)._fetch_dimensions(dataset):
            if dimension.id == "Region":
                yield Dimension(dimension.id,
                                datatype="region",
                                dialect="skatteverket",
                                label=dimension.label)
            else:
                yield dimension
