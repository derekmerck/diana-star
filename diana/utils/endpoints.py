import attr
import uuid
from dill import dumps

# Diana-agnostic API for get, put, handle endpoints with id's and self-pickling

@attr.s
class Generic(object):
    id = attr.ib(factory=uuid.uuid4)

    @property
    def d(self):
        return dumps(self)


@attr.s
class Item(Generic):
    meta = attr.ib(factory=dict)
    data = attr.ib(repr=False, default=None)


@attr.s
class Endpoint(Generic):
    location = attr.ib(default=None)
    inventory = attr.ib(default=None)

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def put(self, *args, **kwargs):
        raise NotImplementedError

    def handle(self, item, instruction, *args, **kwargs):
        raise NotImplementedError

