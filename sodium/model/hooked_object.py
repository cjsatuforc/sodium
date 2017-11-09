"""
Defines a hooked object, which wraps an object while hooking in some external code which can replace properties
and methods in the object.

Usage:

To return the value of "baz" every time "bar" is accessed:
    HookedObject(foo, (lambda x: x == 'bar', lambda x: x.baz))

To return an external value for "bar" in all cases:
    var baz = ...
    HookedObject(foo, (lambda x: x == 'bar', lambda _: baz))

Each hook is a 2-tuple that consists of a test of the name being accessed and a function get the appropriate value.

"""


class HookedObject:
    def __init__(self, obj, hook, *rest):
        self._obj = obj
        self._hooks = [hook] + list(rest)

    def __getattr__(self, name):
        return next((h(self._obj) for p, h in self._hooks if p(name)), getattr(self._obj, name))

    def __setattr__(self, key, value):
        if key == '_obj' or key == '_hooks':
            super(HookedObject, self).__setattr__(key, value)
        else:
            setattr(self._obj, key, value)

