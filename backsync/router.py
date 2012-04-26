import logging
import json
from sockjs.tornado import SockJSConnection

class BacksyncModelRouter(SockJSConnection):
    listeners = set()
    MODELS = {}

    @classmethod
    def register(cls, name, handler):
        cls.MODELS[name] = handler

    def instance(self, name):
        return self.MODELS.get(name, None)

    def on_open(self, request):
        self.listeners.add(self)

        for cls in self.MODELS.values():
            obj = cls(self.session)
            if hasattr(obj, 'on_open'):
                obj.on_open()

    def on_close(self):
        for cls in self.MODELS.values():
            obj = cls(self.session)
            if hasattr(obj, 'on_close'):
                obj.on_close()

        self.listeners.remove(self)

    def on_message(self, message):
        """
        """
        try:
            msg = json.loads(message)
        except :
            pass

        model, method = msg['event'].split(':', 1)

        cls = self.instance(model)
        obj = cls(self.session)

        data  = msg.get('data', None)
        txid  = msg.get('id', None)

        logging.debug("[%s] EVENT = %s:%s  DATA = %r" % (txid, model, method, data))

        func = getattr(obj, method)
        result = None

        if func:
            if data is None:
                result = func()
            else:
                result = func(**data)
        else:
            logging.info("Missing method on %s for %s" % (model, method))

        if txid:
            response = {
                'id'    : txid,
                'event' : '%s:%s' %  (model, method),
                'data'  : (None, result),
            }
            print response
            self.send(response)
