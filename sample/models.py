import logging
import uuid

import backsync
from .mock_model import BackModel, Field

class ChatUser(BackModel):
    meta = {
        'sync_name' : 'User',
    }

    id         = Field(default=lambda:str(uuid.uuid4()))
    screenName = Field(default='Anonymous')

class ChatMessage(BackModel):
    id         = Field(default=lambda:str(uuid.uuid4()))
    userId     = Field()
    message    = Field(default='')
    color      = Field(default='black')
    screenName = Field(default='anonymous')

    #def save(self, *args, **kwargs):
    #    self.objects.upsert(self.id, self)
    #    super(ChatMessage, self).save(*args, **kwargs)

    #def delete(self, *args, **kwargs):
    #    self.objects.delete(self.id, self)
    #    super(ChatMessage, self).destroy(*args, **kwargs)

ChatMessage(message="message one").save()
ChatMessage(message="message two").save()
ChatMessage(message="message three").save()

#
#
#
@backsync.router('User')
class UserHandler(backsync.BacksyncHandler):
    SESSIONS = {}

    def read(self, *args, **kwargs):
        print "UserHandler - READ..."
        return [obj.serialize() for obj in ChatUser.objects.all()]

    def upsert(self, *args, **kwargs):
        print "UserHandler - UPSERT..."
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
        print "DELETE..."

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
        print "Connection OPENED"

    def on_close(self):
        print "Connection CLOSED"
        if self.session in self.SESSIONS:
            obj = self.SESSIONS.pop(self.session)
            obj.delete()

@backsync.router('ChatMessage')
class MessageHandler(backsync.BacksyncHandler):
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
