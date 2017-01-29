#!/usr/bin/env python3
# *-_-* coding: utf-8 *-_-*


import gevent
from gevent import monkey; monkey.patch_all()

import urllib
from bs4 import Beautiful

class LiteroticaArticle:
    """obtain an article from literotica.com"""
    def __init__(self, url):
        assert url.startswith('https://www.literotica.com/s/')
        self.url = url

    def get_page(self):
        urllib.URLopener()

