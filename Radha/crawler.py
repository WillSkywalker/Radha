#!/usr/bin/env python3
# *-_-* coding: utf-8 *-_-*


import gevent
from gevent import monkey; monkey.patch_all()

import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup


cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))


class LiteroticaArticle:
    """obtain an article from literotica.com"""

    def __init__(self, url):
        assert url.startswith('https://www.literotica.com/s/')
        self.url = url
        # self.queue = gevent.Queue()

    def get_article(self):
        r = opener.open(self.url).read()
        soup = BeautifulSoup(r.decode(), 'lxml')
        pagenum = int(soup.find('span', {'class': 'b-pager-caption-t'}).text.split()[0])
        self.article = soup.find('div', {'class': 'b-story-body-x'}).div.p.text

        a = gevent.joinall([gevent.spawn(self._get_page, i)
                            for i in range(2, pagenum+1)], timeout=10)
        self.article += ''.join(map(lambda x: x[1], sorted((t.value for t in a),
                                                            key=lambda x: x[0])))
        # a = [self._get_page(i) for i in range(2, pagenum+1)]
        # self.article += ''.join(map(lambda x: x[1], sorted(a, key=lambda x: x[0])))

        return self.article

    #TODO
    def generate_html(self):
        pass

    def _get_page(self, num):
        r = opener.open(self.url+'?page={0}'.format(num)).read()
        soup = BeautifulSoup(r.decode(), 'lxml')
        article = soup.find('div', {'class': 'b-story-body-x'}).div.p.text
        return (num, article)


class PageGenerator:
    """generate a static page"""
    def __init__(self, arg):
        super(PageGenerator, self).__init__()
        self.arg = arg


if __name__ == '__main__':
    t = LiteroticaArticle('https://www.literotica.com/s/female-sexual-response-subject-326')
    a = t.get_article()
    with open('test.txt', 'w') as fh:
        fh.write(a)
