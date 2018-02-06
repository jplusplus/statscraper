# encoding: utf-8
""" A wrapper around the SCB API, demonstrating how to extend
    a scraper in the scraper park.
"""
from .PXWebScraper import PXWeb, Dimension
import requests


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

    def _fetch_data(self, dataset, query, filtertype="item"):
        """
         Override to translate region values.
        """
        for data in super(SCB, self)._fetch_data(dataset, query, filtertype="item"):
            # This is a hack. The basescraper should provide an interface for
            # translating _from_ dialects in cases like this,
            # e.g. a _reverse_translate_ method
            if "Region" in data.raw_dimensions:
                rregion = data.raw_dimensions["Region"]
            # import pdb;pdb.set_trace();
                for translation in self.current_item.dimensions["Region"].datatype.allowed_values:
                    if "skatteverket" in translation.dialects and translation.dialects["skatteverket"] == rregion:
                        rregion = translation.value
                data.raw_dimensions["Region"] = rregion
            yield data
