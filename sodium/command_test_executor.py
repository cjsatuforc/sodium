"""

"""

import adsk.core
import traceback

from .model.hooked_object import HookedObject
from .model.command_input_tracker import CommandInputTracker


class CommandTestExecutor(adsk.core.CommandCreatedEventHandler):

    class DestroyHandler(adsk.core.CommandEventHandler):
        def __init__(self, fn):
            super().__init__()
            self._fn = fn

        def notify(self, args):
            print('on destroy, calling fn!')
            self._fn()

    class ActivateHandler(adsk.core.CommandEventHandler):
        def __init__(self, inputs, run_test_fn, finalize):
            super().__init__()
            self._inputs = inputs
            self._run_test_fn = run_test_fn
            self._finalize = finalize

        def notify(self, args):
            try:
                self._run_test_fn(args.command, self._inputs)
                self._finalize(True, None)
            except Exception as e:
                traceback.print_exc()
                self._finalize(False, e)

    def __init__(self, commandCreated):
        super().__init__()
        self._commandCreated = commandCreated
        self._inputs = {}
        self._handlers = []
        self._test_run_fn = None
        self._test_finish_fn = None
        self._test_destroy_fn = None

    def on_test_run(self, fn):
        self._test_run_fn = fn

    def on_test_finish(self, fn):
        self._test_finish_fn = fn

    def on_test_destroy(self, fn):
        self._test_destroy_fn = fn

    def notify(self, args):
        try:
            print('in TestableCommandCreatedEventHandler')
            command = args.command
            hcommand = HookedObject(args.command, (lambda x: x == 'commandInputs', lambda x: CommandInputTracker(x.commandInputs, self._inputs)))
            hargs = HookedObject(args, (lambda x: x == 'command', lambda _: hcommand))
            print(command.activate)
            ret = self._commandCreated.notify(hargs)

            onActivate = CommandTestExecutor.ActivateHandler(self._inputs, self._test_run_fn, self._test_finish_fn)
            command.activate.add(onActivate)
            self._handlers.append(onActivate)

            onDestroy = CommandTestExecutor.DestroyHandler(self._test_destroy_fn)
            command.destroy.add(onDestroy)
            self._handlers.append(onDestroy)
            return ret
        except Exception as e:
            traceback.print_exc()
            self._finalize(False, e)
