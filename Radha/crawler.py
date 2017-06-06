#!/usr/bin/env python3
# *-_-* coding: utf-8 *-_-*


import gevent
from gevent import monkey
monkey.patch_all()

import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import Session

# import redis
from celery import Celery

from models import EroticArticle, Paragraph
from config import Config

cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, encoding='utf-8')
mq = Celery(__name__, broker='redis://localhost')


class LiteroticaArticle:
    """obtain an article from literotica.com"""

    def __init__(self, url):
        assert url.startswith('https://www.literotica.com/s/')
        self.url = url
        self.db_session = Session(db_engine)
        # self.queue = gevent.Queue()
        if self.db_session.query(exists().where(EroticArticle.url == url)).scalar():  # Article exists
            self.get_article = lambda: None
            self.add_to_database = lambda: None

    def get_article(self):
        r = opener.open(self.url).read()
        soup = BeautifulSoup(r.decode(), 'lxml')
        self.pagenum = int(soup.find('span', {'class': 'b-pager-caption-t'}).text.split()[0])
        self.article = soup.find('div', {'class': 'b-story-body-x'}).div.p.text
        self.title = soup.find('div', {'class': 'b-story-header'}).h1.text
        self.category = soup.find('div', {'class': 'b-breadcrumbs'}).find_all('a')[1].text
        self.tags = ''
        a = gevent.joinall([gevent.spawn(self._get_page, i)
                            for i in range(2, self.pagenum+1)], timeout=10)
        self.article += ''.join(map(lambda x: x[1], sorted((t.value for t in a),
                                key=lambda x: x[0])))
        # a = [self._get_page(i) for i in range(2, pagenum+1)]
        # self.article += ''.join(map(lambda x: x[1], sorted(a, key=lambda x: x[0])))

        return self.article

    #TODO
    def to_json(self):
        return self.__dict__

    def add_to_database(self):
        post = EroticArticle(title=self.title,
                             category=self.category,
                             tags=self.tags,
                             url=self.url,
                             viewcount=0)
        self.db_session.add(post)
        self.db_session.commit()

        for idx, para in enumerate(self.article.split('\n')):
            if para:
                self.db_session.add(Paragraph(content=para, art_id=post.id, para_idx=idx))
        self.db_session.commit()

    def _get_page(self, num):
        r = opener.open(self.url+'?page={0}'.format(num)).read()
        soup = BeautifulSoup(r.decode(), 'lxml')
        article = soup.find('div', {'class': 'b-story-body-x'}).div.p.text
        if num == self.pagenum:
            self.tags = soup.find('div', {'class': 'b-s-story-tag-list'}).ul.text
        return (num, article)


@mq.task
def save_article(url):
    art = LiteroticaArticle(url)
    art.get_article()
    art.add_to_database()


if __name__ == '__main__':
    t = LiteroticaArticle('https://www.literotica.com/s/hunted-1')
    a = t.get_article()
    t.add_to_database()
