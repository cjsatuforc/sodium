"""
    A CommandCreatedEventHandler implementation that runs a test for a command definition.  This is implemented
    as a CommandCreatedEventHandler so we can attach ourselves to any command definition, look up the inputs that the
    command definition created, and then inject handlers to run the test and report the results.
"""

import adsk.core
import traceback

from ..helper.function_destroy_handler import FunctionDestroyHandler


class CommandTestExecutor(adsk.core.CommandCreatedEventHandler):

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
            command = args.command
            # Pull all of the inputs into a map
            self._inputs = {i.id: i for i in command.commandInputs}
            onActivate = CommandTestExecutor.ActivateHandler(self._inputs, self._test_run_fn, self._test_finish_fn)
            command.activate.add(onActivate)
            self._handlers.append(onActivate)

            onDestroy = FunctionDestroyHandler(self._test_destroy_fn)
            command.destroy.add(onDestroy)
            self._handlers.append(onDestroy)
        except Exception as e:
            traceback.print_exc()
            self._finalize(False, e)
