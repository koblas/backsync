import tornado.web

# Trigger the registration of the Models
import models

class ChatHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("chat.html")

