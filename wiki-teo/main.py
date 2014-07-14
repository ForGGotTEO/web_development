import webapp2
import handlers

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'


handlers = [('/signup', handlers.RegistrationHandler),
            ('/login', handlers.LoginHandler),
            ('/logout', handlers.LogoutHandler),
            ('/edit' + PAGE_RE, handlers.EditViewHandler),
            ('/history' + PAGE_RE, handlers.HistoryHandler),
            (PAGE_RE, handlers.DetailViewHandler)]


app = webapp2.WSGIApplication(handlers, debug=True)
