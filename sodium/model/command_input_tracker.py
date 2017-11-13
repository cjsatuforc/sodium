"""

    A CommandInputs-like object that holds a reference to every input created by the caller.  This is used
    to track inputs created in command creation code, so we can query/set them as part of the test.

    This class is intended to be used as part of a HookedObject passed into a command handler, but could
    also be used for stubbing/mocking, for testing UI builder code.

    DEPRECATED: This class represents an old way of hooking into a command, and is no longer used.  It's kept around
    for now just in case we need it.
"""

import adsk.core

class CommandInputTracker:
    def __init__(self, commandInputs, inputs=None):
        #print('TestableCommandInputs created: %s, %s' % (str(commandInputs), str(inputs)))
        self._commandInputs = commandInputs
        if inputs is not None:
            self._inputs = inputs
        else:
            self._inputs = {}

    def __getattr__(self, name):
        f = getattr(self._commandInputs, name)
        if f is None:
            return None

        if isinstance(f, adsk.core.CommandInputs):
            print('comamnd inputs!')
            return CommandInputTracker(f, self._inputs)
        elif name.startswith('add'):
            def wrapped(*args, **kwargs):
                id = args[0]
                inpt = f(*args, **kwargs)
                if isinstance(id, str):
                    self._inputs[id] = inpt
                    if name.startswith('addTab') or name.startswith('addGroup'):
                        print("returning more of a thing")
                        inpt = CommandInputTracker(inpt, self._inputs)
                return inpt

            return wrapped
        else:
            return f

    def __setattr__(self, key, value):
        if key == "_commandInputs" or key == "_inputs":
            super(CommandInputTracker, self).__setattr__(key, value)
        else:
            setattr(self._commandInputs, key, value)

    def print_testable_inputs(self):
        print(str([k for k in self._inputs]))
