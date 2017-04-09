from flask.ext.sqlalchemy import SQLAlchemy


class Article(object):
    """docstring for Article"""
    def __init__(self, arg):
        super(Article, self).__init__()
        self.arg = arg

