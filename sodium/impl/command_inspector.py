
import adsk.core
from ..helper.function_destroy_handler import FunctionDestroyHandler


class CommandInspector(adsk.core.CommandCreatedEventHandler):

    def __init__(self, ids=None):
        super().__init__()
        self._close_callback = None
        self._handlers = []
        if ids is None:
            ids = []
        self._ids = ids

    def set_close_callback(self, cb):
        self._close_callback = cb

    def notify(self, args):
        command = args.command
        # All we want to do is inspect the command form, not run it
        # TODO: this may change the command for future runs....shouldn't, since it's not in the
        # definition but we may need to cache the original result and restore it in the destroy handler
        command.isAutoExecute = False
        command.isExecutedWhenPreEmpted = False

        for i in command.commandInputs:
            self._ids.append(i.id)

        # Add a destroy handler to let the calling code clean up after itself
        destroy = FunctionDestroyHandler(self._close_callback)
        command.destroy.add(destroy)
        self._handlers.append(destroy)



