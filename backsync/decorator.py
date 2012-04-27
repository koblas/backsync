from .router import BacksyncModelRouter

class router(object):
    """Decorator"""

    def __init__(self, name=None):
        self.name = name

    def __call__(self, klass):
        name = self.name or klass.__name__
        self.klass = klass
        BacksyncModelRouter.register(name, klass)
        klass._sync_name = name
        return klass
