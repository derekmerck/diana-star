# Redirect Diana base-class imports here to wrap celery get/put/handle
# calls with oo calls.  Or add "DistribMixin" to custom classes.

from ..connect.apis import *
from .tasks import *
import attr


def star(func):
    def wrapper(self, *args, **kwargs):
        celery_args = {}
        if self.queue:
            celery_args['queue'] = self.queue
        if not kwargs:
            kwargs = {}
        kwargs['pattern'] = self.p
        kwargs['method'] = func.__name__
        return do.apply_async(args, kwargs, **celery_args)
    return wrapper


# Not super-elegant, but any starxxx func should also have an xxx_s sig func
def star_s(func):
    def wrapper(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        kwargs['pattern'] = self.p
        kwargs['method'] = func.__name__[:-2]
        return do.s(*args, **kwargs).set(queue=self.queue)
    return wrapper


@attr.s
class DistribMixin(object):
    queue = attr.ib(default=None)  # Can set a queue name per class

    @star
    def get(self, *args, **kwargs): pass
    @star_s
    def get_s(self, *args, **kwargs): pass
    @star
    def put(self, *args, **kwargs): pass
    @star_s
    def put_s(self, *args, **kwargs): pass


@attr.s
class OrthancEndpoint(DistribMixin, OrthancEndpoint):

    @star
    def clear(self, *args, **kwargs): pass
    @star_s
    def clear(self, *args, **kwargs): pass
    @star
    def anonymize(self, *args, **kwargs): pass
    @star_s
    def anonymize_s(self, *args, **kwargs): pass
    @star
    def find(self, *args, **kwargs): pass
    @star_s
    def find_s(self, *args, **kwargs): pass


@attr.s
class SplunkEndpoint(DistribMixin, SplunkEndpoint):

    @star
    def find(self, *args, **kwargs): pass
    @star_s
    def find_s(self, *args, **kwargs): pass


@attr.s
class RedisEndpoint(DistribMixin, RedisEndpoint):
    pass


@attr.s
class ClassificationEndpoint(DistribMixin, ClassificationEndpoint):
    queue = attr.ib(default="learn")

    @star
    def classify(self, *args, **kwargs): pass
    @star_s
    def classify_s(self, *args, **kwargs): pass


@attr.s
class FileEndpoint(DistribMixin, FileEndpoint):
    queue = attr.ib(default="file")
