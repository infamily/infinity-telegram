# coding: utf-8
"""Infty2.0 REST API client"""
from coreapi import Client


class Schema(object):
    def __init__(self, url):
        self.client = Client()
        self.url = url
        self.schema = self.client.get(self.url)
