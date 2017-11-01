# coding: utf-8
"""Infty2.0 REST API client"""
import slumber

from inftybot import config


class API(object):
    """
    Class for acessing Infty REST API
    """
    def __init__(self, base_url=None, **kwargs):
        self.base_url = base_url or config.INFTY_API_URL
        self.client = slumber.API(self.base_url, **kwargs)
