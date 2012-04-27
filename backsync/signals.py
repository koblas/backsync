from blinker import Namespace

__all__ = ['pre_save', 'post_save', 'pre_delete', 'post_delete']

signals = Namespace()

# NOT USED : pre_init    = signals.signal('pre_init')
# NOT USED : post_init   = signals.signal('post_init')

pre_save    = signals.signal('pre_save')
post_save   = signals.signal('post_save')
pre_delete  = signals.signal('pre_delete')
post_delete = signals.signal('post_delete')
