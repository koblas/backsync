from .decorator import backsync
from .handler import BacksyncHandler
from .router import BacksyncModelRouter
from sockjs.tornado import SockJSRouter

BacksyncRouter = SockJSRouter(BacksyncModelRouter, '/backsync')
