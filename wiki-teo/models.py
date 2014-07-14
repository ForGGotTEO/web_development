import utils

from google.appengine.ext import db


class Page(db.Model):
    url = db.StringProperty()
    body = db.TextProperty()

    @classmethod
    def get_by_url(cls, url):
            return Page.all().filter('url = ', url).get()


class User(db.Model):
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def get_by_name(cls, name):
        return User.all().filter('username =', name).get()

    @classmethod
    def register(cls, username, pw, email=None):
        pw_hash = utils.make_pw_hash(username, pw)
        return User(username=username, pw_hash=pw_hash, email=email)
