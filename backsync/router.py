import logging
import json
from sockjs.tornado import SockJSConnection
from backsync import signals

class BacksyncModelRouter(SockJSConnection):
    listeners = set()
    active_session = None
    MODELS = {}

    @classmethod
    def register(cls, name, handler):
        cls.MODELS[name] = handler

    def instance(self, name):
        return self.MODELS.get(name, None)

    def on_open(self, request):
        self.listeners.add(self)
        self.__class__.active_session = self

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
        if self.listeners:
            s = self.listeners.pop()
            self.listeners.add(s)
        else :
            s = None
        self.__class__.active_session = s

    def on_message(self, message):
        """
        """
        try:
            msg = json.loads(message)
        except :
            pass

        model, method = msg['event'].split(':', 1)
        txid  = msg.get('id', None)

        result = None
        error = None

        cls = self.instance(model)
        if cls is None:
            logging.warning("Unable to locate model handler for: %s" % model)
            error = "Unable to locate model handler for: %s" % model
        else:
            obj = cls(self.session)

            data  = msg.get('data', None)

            logging.debug("[%s] EVENT = %s:%s  DATA = %r" % (txid, model, method, data))

            func = getattr(obj, method)

            try :
                if func:
                    if data is None:
                        result = func()
                    else:
                        result = func(**data)
                else:
                    logging.info("Missing method on %s for %s" % (model, method))
                    error = 'Missing Method %s:%s' % (model, method)
            except Exception as e:
                error = 'EXCEPTION: %s' % (e)

        if txid:
            response = {
                'id'    : txid,
                'event' : '%s:%s' %  (model, method),
                'data'  : result,
            }
            if error :
                response['error'] = error
            self.send(response)

    @classmethod
    def post_save(cls, model, instance=None):
        logging.debug("In post save handler model = %s" % (model))
        name = getattr(model, 'sync_name', model.__name__)
        message = {'event': "%s:%s" % (name, 'upsert'), 'data' : instance.serialize()}
        if cls.active_session:
            cls.active_session.broadcast(BacksyncModelRouter.listeners, message)

    @classmethod
    def post_delete(cls, model, instance=None):
        logging.debug("In post delete handler model = %s" % (model))
        name = getattr(model, 'sync_name', model.__name__)
        message = {'event': "%s:%s" % (name, 'delete'), 'data' : instance.serialize()}
        if cls.active_session:
            cls.active_session.broadcast(BacksyncModelRouter.listeners, message)

signals.post_save.connect(BacksyncModelRouter.post_save)
signals.post_delete.connect(BacksyncModelRouter.post_delete)
