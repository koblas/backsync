from .decorator import router
from .handler import BacksyncHandler
from .router import BacksyncModelRouter
from sockjs.tornado import SockJSRouter

BacksyncRouter = SockJSRouter(BacksyncModelRouter, '/backsync')
