#!/usr/bin/env python3
# -_- coding: utf-8 -_-

from flask import Flask
from flask import jsonify
from flask.ext.script import Manager

from flask_cors import CORS, cross_origin

import urllib.request
import http.cookiejar
import json
import redis


app = Flask(__name__)
manager = Manager(app)
CORS(app)
RED = redis.StrictRedis()


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
    except KeyError:
        definition = '暂无释义...'
    RED.set('word:'+name, definition)
    # return json.loads(r)
    return definition


if __name__ == '__main__':
    manager.run()
