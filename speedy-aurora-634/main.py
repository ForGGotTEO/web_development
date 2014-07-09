import webapp2
import cgi

form ="""
<form method = "post">
        What is your birthday?
        <br>
        <label>Day <input type = "text" name = "day" value = "%(day)s"></label>
        <label>Month <input type = "text" name = "month" value = "%(month)s"></label>
        <label>Year <input type = "text" name = "year" value = "%(year)s"></label>
        <div style = "color: red">%(error)s</div>
        <br>
        <br>
        <input type = "submit">
</form>
"""

class MainPage(webapp2.RequestHandler):
    def write_form(self,error = "",day = "",month = "",year = ""):
        self.response.out.write(form % {"error": error,
                                        "day": escape_html(day),
                                        "month": escape_html(month),
                                        "year": escape_html(year)})
    
    def get(self):
        self.write_form()

    def post(self):
        user_day =  self.request.get('day')
        user_month = self.request.get('month')
        user_year = self.request.get('year')

        day = valid_day(user_day)
        month = valid_month(user_month)
        year = valid_year(user_year)

        if not (day and month and year):
            self.write_form("Sorry, that date isn't valid.",
                            user_day,user_month,user_year)
        else:
            self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! That's a valid date.")
   
app = webapp2.WSGIApplication([('/', MainPage), ('/thanks', ThanksHandler)], debug=True)
