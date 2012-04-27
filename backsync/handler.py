import logging
from .router import BacksyncModelRouter

class BacksyncHandler(object):
    model = None

    def __init__(self, session):
        self.session = session

    def read(self, *args, **kwargs):
        return [msg.serialize() for msg in self.model.find()]

    def upsert(self, *args, **kwargs):
        obj = self.model.find(**kwargs)
        if obj is None:
            obj = self.model(*args, **kwargs)
        else:
            obj.set(**kwargs)
        obj.save()

        s = obj.serialize()
        self.notify("%s:upsert" % self._sync_name, s)
        return s

    def delete(self, *args, **kwargs):
        obj = self.model.find(**kwargs)
        obj.destroy(**kwargs)
        self.notify("%s:delete" % self._sync_name, s)
        return {}

    def notify(self, method, data):
        message = {'event': "%s:%s" % (self._sync_name, method), 'data' : data}
        logging.debug("Sending Notification %s" % message['event'])
        self.session.broadcast(BacksyncModelRouter.listeners, message)
