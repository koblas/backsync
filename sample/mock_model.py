import logging
from collections import defaultdict, OrderedDict

# from blinker import Signal

import backsync

STORE = defaultdict(OrderedDict)

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

class QuerySetManager():
    """Query set manager that mimics bigger behavior, but just keeps everything in a dictonary"""

    def __init__(self, store=None):
        self.store = store

    def all(self, *args, **kwargs):
        return [v for v in self.store.values()]

    def get(self, id):
        return self.store.get(id, None)

    def _upsert(self, id, value):
        """ Not really a public interface - used by the BackModel object """
        self.store[id] = value

    def _delete(self, id):
        """ Not really a public interface - used by the BackModel object """

        del self.store[id]

class BackMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(BackMetaclass, cls).__new__

        base_meta = getattr(cls, 'meta', {})

        meta = {
            'sync_name' : name,
        }
        meta.update(base_meta)

        meta.update(attrs.get('meta', {}))
        if 'store' not in meta:
            meta['store'] = STORE[meta.get('sync_name')]
        attrs['_meta'] = meta

        attrs['sync_name'] = meta['sync_name']

        #new_class = super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)

        # Set some of the properties of interest
        new_class.objects = attrs.get('objects', meta.get('objects', QuerySetManager(meta['store'])))

        new_class._fields = {}
        for field in dir(new_class):
            v = getattr(new_class, field)
            if isinstance(v, Field):
                new_class._fields[field] = v

        return new_class


class BackModel(object):
    """Pretending to be a Mongoengine Model or a Django Model style interface to objects.  Though
       it has a little bit of Backbone mixed in for good luck.
    """

    __metaclass__ = BackMetaclass

    _isNew    = True

    def __init__(self, *args, **kwargs):
        for name, v in self._fields.items():
            if hasattr(v, 'default') and callable(v.default):
                setattr(self, name, v.default())
            else:
                setattr(self, name, getattr(v, 'default', None))

        self.set(**kwargs)

    def set(self, *args, **kwargs):
        for field, value in kwargs.items():
            if field in self._fields:
                setattr(self, field, value)
        return self

    def save(self, *args, **kwargs):
        self.objects._upsert(self.id, self)

        backsync.signals.post_save.send(self.__class__, instance=self)

    def delete(self, *args, **kwargs):
        self.objects._delete(self.id)

        backsync.signals.post_delete.send(self.__class__, instance=self)

    def validate(self, **kwargs):
        return None

    def serialize(self):
        data = {}
        for field in self._fields:
            data[field] = getattr(self, field)
        return data
