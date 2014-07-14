import os
import time
import re
import webapp2
import jinja2
import logging

import models
import utils

from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(kwargs)


class SignupHandler(Handler):
    
    def unique_username(self, username):
        if not models.User.get_by_name(username):
            return True

    def valid_username(self, username):
        USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
        return USER_RE.match(username)

    def valid_pw(self, password):
        PASSWORD_RE = re.compile(r'^.{3,20}$')
        return PASSWORD_RE.match(password)

    def valid_email(self, email):
        EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
        return EMAIL_RE.match(email)

    def login(self, user):
        user_hash = utils.make_secure_val(str(user.key().id()))
        self.response.set_cookie('user_id', value=user_hash)

    def logout(self):
        self.response.set_cookie('user_id', value='')


class RegistrationHandler(SignupHandler):
    """Handles site registration for users."""
    def render_form(self, **kwargs):
        self.render("register.html", **kwargs)

    def get(self):
        self.render_form()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        err_usr = ''
        err_unq = ''
        err_pass1 = ''
        err_pass2 = ''
        err_email = ''

        if not self.unique_username(username):
            err_unq = "That name already exists!"

        if not self.valid_username(username):
            err_usr = "That's not a valid username."

        if not self.valid_pw(password):
            err_pass1 = "That's not a valid password."
        elif password != verify:
            err_pass2 = "Your passwords don't match."

        if len(email) != 0 and not self.valid_email(email):
            err_email = "That's not a valid email address"

        if err_usr or err_unq or err_pass1 or err_pass2 or err_email:
            self.render_form(username=username, email=email, err_usr=err_usr,
                             err_unq=err_unq, err_pass1=err_pass1,
                             err_pass2=err_pass2, err_email=err_email)
        else:
            u = models.User.register(username=username, pw=password, email=email)
            u.put()
            self.login(u)
            self.redirect("/")


class LoginHandler(SignupHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        err_usr = ''
        err_pass = ''

        try:
            user = models.User.get_by_name(username)
            if not user:
                err_usr = "username doesn't exist"

            if not utils.valid_password(username, password, user.pw_hash):
                err_pass = "invalid password"

            if err_usr or err_pass:
                self.render("login.html", err_usr=err_usr, err_pass=err_pass, username=username)
            else:
                self.login(user)
                self.redirect("/")
        except AttributeError:
            self.redirect("/signup")


class LogoutHandler(SignupHandler):

    def get(self):
        self.logout()
        self.redirect("/signup")


class EditViewHandler(Handler):

    def render_form(self, url='', body='', **kwargs):
        self.render("edit_page.html", url=url, body=body, **kwargs)

    def get(self, slug):
        try:
            u_cookie = self.request.cookies.get("user_id")
            try:
                user = models.User.get_by_id(int(u_cookie.split("|")[0]))
                if user:
                    p = models.Page.get_by_url(slug)
                    self.render_form(url=slug, page=p)
            except AttributeError:
                self.redirect("/signup")
        except ValueError:
            self.redirect("/signup")

    def post(self, slug):
        body = self.request.get("content")
        url = slug

        try:
            u_cookie = self.request.cookies.get("user_id")
            try:
                user = models.User.get_by_id(int(u_cookie.split("|")[0]))
                if user:
                    p = models.Page.get_by_url(url)
                    if not p:
                        p = models.Page(body=body, url=url)
                        p.put()
                        utils.cache_detail_view(slug, update=True)
                        self.redirect("{0}".format(url))
                    else:
                        p.body = body
                        p.put()
                        utils.cache_detail_view(slug, update=True)
                        self.redirect("{0}".format(url))
                else:
                    self.redirect("/signup")
            except AttributeError:
                self.redirect("/signup")
        except ValueError:
            self.redirect("/signup")


class DetailViewHandler(Handler):

    def get(self, slug):
        p = utils.cache_detail_view(slug)
        cache_time = memcache.get("detail_cache_" + slug)
        query_time = int(time.time() - cache_time)

        try:
            u_cookie = self.request.cookies.get("user_id")
            try:
                user = models.User.get_by_id(int(u_cookie.split("|")[0]))
                if user:
                    if not p:
                        self.redirect('/edit{0}'.format(slug))
                    else:
                        self.render("page_detail.html", page=p, query_time=query_time, login=True)
            except AttributeError:
                if not p:
                    self.redirect("/signup")
                else:
                    self.render("page_detail.html", page=p, query_time=query_time, login=False)
        except ValueError:
            if not p:
                self.render("page_detail.html", page=p, login=False)
            else:
                self.redirect("/signup")


class HistoryHandler(Handler):
    def get(self, slug):
        p = db.GqlQuery("SELECT * FROM Page WHERE url = :1 ORDER BY revision DESC", slug)

        try:
            u_cookie = self.request.cookies.get("user_id")
            try:
                user = models.User.get_by_id(int(u_cookie.split("|")[0]))
                if user:
                        self.render("page_history.html", pages=p, login=True)
            except AttributeError:
                if not p:
                    self.redirect("/signup")
        except ValueError:
            self.redirect("/signup")
