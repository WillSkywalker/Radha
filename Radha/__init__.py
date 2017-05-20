#!/usr/bin/env python3
# -_- coding: utf-8 -_-

from flask import Flask
from flask import jsonify

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

import urllib.request
import http.cookiejar
import json
import redis

from .config import Config
from .models import metadata, EroticArticle, Paragraph, Translation


app = Flask(__name__)
app.config.from_object(Config)
manager = Manager(app)
CORS(app)
db = SQLAlchemy(metadata=metadata)
db.init_app(app)
RED = redis.StrictRedis()
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))


@app.route('/api/word/<name>')
@cross_origin()
def word(name):

    if RED.exists('word:'+name):
        return RED.get('word:'+name)

    r = opener.open('https://api.shanbay.com/bdc/search/?word=%s' % name).read()
    try:
        definition = json.loads(r)['data']['definition']
        RED.set('word:'+name, definition)
    except KeyError:
        definition = '暂无释义...'
        RED.set('word:'+name, '暂无释义...', ex=3600)
    # return json.loads(r)
    return definition


def get_article(idx):
    # EroticArticle.
    pass


# if __name__ == '__main__':
#     manager.run()
