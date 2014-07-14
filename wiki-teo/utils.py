import hmac
import time
import logging
import hashlib
import random
import string

import models

from google.appengine.api import memcache

SECRET = '17cOWkF6K6WS6YWJV4LMlrKkygK4gH'


def make_secure_val(val):
    return "{0}|{1}".format(val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(h):
    val = h.split("|")[0]
    if h == make_secure_val(val):
        return val


def make_salt():
    return "".join(random.choice(string.letters) for i in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    hashed_val = hashlib.sha256(name + pw + salt).hexdigest()
    return '{0}|{1}'.format(salt, hashed_val)


def valid_password(name, pw, h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name, pw, salt)


def cache_detail_view(slug, update=False):
    key = slug
    t_key = 'detail_cache_' + slug
    p = memcache.get(key)
    if p is None or update:
        logging.error("DB QUERY")
        p = models.Page.get_by_url(slug)
        memcache.set(key, p)
        memcache.set(t_key, time.time())
    return p
