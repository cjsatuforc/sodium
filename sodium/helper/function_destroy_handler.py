"""

"""

import adsk.core

class FunctionDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self, fn):
        super().__init__()
        self._fn = fn

    def notify(self, args):
        print('on destroy, calling fn!')
        self._fn()
