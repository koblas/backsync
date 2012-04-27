import logging
import backsync
from sample.chat_models import ChatMessage, ChatUser

#
#
#
@backsync.router('User')
class UserHandler(backsync.BacksyncHandler):
    """Manage users - remove them from the active list of users when the session closes"""

    SESSIONS = {}

    def read(self, *args, **kwargs):
        # print "UserHandler - READ..."
        return [obj.serialize() for obj in ChatUser.objects.all()]

    def upsert(self, *args, **kwargs):
        # print "UserHandler - UPSERT..."
        obj = ChatUser.objects.get(kwargs['id'])

        if obj is None:
            obj = ChatUser(*args, **kwargs)
        else:
            obj.set(**kwargs)

        self.SESSIONS[self.session] = obj
        obj.save()

        # self.notify("upsert", obj.serialize())
        return obj.serialize()

    def delete(self, *args, **kwargs):
        # print "DELETE..."

        obj = ChatUser.objects.get(kwargs['id'])
        if obj:
            # Need to delete from session table...
            for k, v in self.SESSIONS.items():
                if v == obj:
                    del self.SESSIONS[k]
                    break
            obj.delete()

        # self.notify("delete", obj.serialize())
        return {}

    def on_open(self):
        logging.debug("Connection OPENED")

    def on_close(self):
        logging.debug("Connection CLOSED")
        if self.session in self.SESSIONS:
            obj = self.SESSIONS.pop(self.session)
            obj.delete()

@backsync.router('ChatMessage')
class MessageHandler(backsync.BacksyncHandler):
    """Pretty simple collection reader"""

    def read(self, *args, **kwargs):
        return [obj.serialize() for obj in ChatMessage.objects.all()]

    def upsert(self, *args, **kwargs):
        obj = ChatMessage.objects.get(kwargs['id'])

        if obj is None:
            obj = ChatMessage(*args, **kwargs)
        else:
            obj.set(**kwargs)

        obj.save()

        return obj.serialize()

    def delete(self, *args, **kwargs):
        obj = ChatMessage.objects.get(kwargs['id'])
        if obj:
            obj.delete()

        return {}
