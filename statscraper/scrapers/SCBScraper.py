"""A wrapper around the SCB API."""
from .PXWebScraper import PXWeb, Dimension


class SCB(PXWeb):
    """The SCB API uses PXWeb. We just hardcode the url."""

    base_url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd'

    def _fetch_dimensions(self, dataset):
        """Yield all dimensions.

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
