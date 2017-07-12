# encoding: utf-8
""" A wrapper around the SCB API, demonstrating how to extend
    a scraper in the scraper park.
"""
from .PXWebScraper import PXWeb


class SCB(PXWeb):

    base_url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd'

    #TODO: Override _fetch_dimensions to set correct datatype and dialect?