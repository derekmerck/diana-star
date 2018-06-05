from .dcelery import app
from diana.connect.apis import DianaFactory

# Note: adding (bind=true) to the decorator provides access to a "self"
# object for introspection.

# This is a much more general task-passing wrapper
# Item always has to be first though, b/c it's the output of the previous
# link in a chain...
@app.task(bind=True)
def do(self, *args, **kwargs):

    pattern = kwargs.get("pattern")
    method = kwargs.get("method")

    del(kwargs["method"])
    del(kwargs["pattern"])

    print("{}:{}.{}".format(self, pattern['service'], method))

    endpoint = DianaFactory.factory(pattern)
    func = endpoint.__getattribute__(method)

    return func(*args, **kwargs)
