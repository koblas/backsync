import logging
import uuid
import time, hashlib
from datetime import datetime

# from blinker import Signal

import backsync

#
#
#
#
class Field(object):
    value   = None
    default = None

    def __init__(self, value=None, default=None):
        self.value = value
        self.default = default

class BackboneModel(object):
    """This model class will mimic the Backbone Model class to make usage more 
       consistent across JavaScript and Python.
    """
    _isNew    = True

    def __init__(self, *args, **kwargs):
        self._fields = {}
        for field in dir(self):
            v = getattr(self, field)
            if isinstance(v, Field):
                self._fields[field] = v
                if hasattr(v, 'default') and callable(v.default):
                    setattr(self, field, v.default())
                else:
                    setattr(self, field, getattr(v, 'default', None))
        self.set(**kwargs)

    def set(self, *args, **kwargs):
        for field, value in kwargs.items():
            if field in self._fields:
                setattr(self, field, value)
        return self

    def save(self, *args, **kwargs):
        # super(Model, self).save(*args, **kwargs)
        isNew = self._isNew
        self._isNew = False
        ## signals.post_save.send(self.__class__, instance=self, created=True)

        # TODO - self.send_update(self, created=isNew)

    def destroy(self, *args, **kwargs):
        pass
        # super(NotifyBase, self).delete(*args, **kwargs)
        ## signals.post_delete.send(self.__class__, instance=self)

        # TODO - self.send_delete(self)

    @classmethod
    def find(self, **kwargs):
        """Find an object based on the object parameters passed"""
        return None

    def validate(self, **kwargs):
        return None

    def serialize(self):
        data = {}
        for field in self._fields:
            data[field] = getattr(self, field)
        return data

#
#
#
class ChatUser(BackboneModel):
    guid     = Field(default=lambda:str(uuid.uuid4()))
    screenName = Field(default='Anonymous')

class ChatMessage(BackboneModel):
    MESSAGES = []
    COUNTER  = 1000

    guid       = Field(default=lambda:str(uuid.uuid4()))
    userId     = Field()
    message    = Field(default='')
    color      = Field(default='black')
    screenName = Field(default='anonymous')

    def save(self, *args, **kwargs):
        self.MESSAGES.append(self)
        super(ChatMessage, self).save(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        self.MESSAGES.remove(self)
        super(ChatMessage, self).destroy(*args, **kwargs)

    @classmethod
    def find(cls, **kwargs):
        guid = kwargs.get('guid')
        if guid:
            for m in cls.MESSAGES:
                if m.guid == guid:
                    return m
            return None
        return cls.MESSAGES

ChatMessage(message="message one").save()
ChatMessage(message="message two").save()
ChatMessage(message="message three").save()

#
#
#
@backsync.backsync('User')
class UserHandler(backsync.BacksyncHandler):
    model = ChatUser
    USERS = {}

    def _find(self, **kwargs):
        guid = kwargs['guid']
        for obj in self.USERS.values():
            if guid == obj.guid:
                return obj
        return None

    def read(self, *args, **kwargs):
        print "READ...", self.USERS.values()
        return [obj.serialize() for obj in self.USERS.values()]

    def upsert(self, *args, **kwargs):
        print "UPSERT...", self.USERS.values()
        obj = self._find(**kwargs)
        if obj is None:
            obj = self.model(*args, **kwargs)
        else:
            obj.set(**kwargs)


        self.USERS[self.session] = obj

        obj.save()

        self.notify("upsert", obj.serialize())
        return obj.serialize()

    def delete(self, *args, **kwargs):
        print "DELETE...", self.USERS.values()
        obj = self._find(**kwargs)
        if obj:
            obj.destroy(**kwargs)
            for k, v in self.USERS.items():
                if v == obj:
                    del self.USERS[k]
                    break

        self.notify("delete", obj.serialize())
        return {}

    def on_open(self):
        print "Connection OPENED"

    def on_close(self):
        print "Connection CLOSED"
        if self.session in self.USERS:
            self.USERS[self.session].delete()

@backsync.backsync('ChatMessage')
class MessageHandler(backsync.BacksyncHandler):
    model = ChatMessage

    def upsert(self, *args, **kwargs):
        v = super(MessageHandler, self).upsert(*args, **kwargs)
        self.notify("ChatMessage:upsert", v)
        return v

    def delete(self, *args, **kwargs):
        v = super(MessageHandler, self).delete(*args, **kwargs)
        self.notify("ChatMessage:upsert", v)
        return v
