
import traceback
import uuid

import adsk.core
from .impl import CommandTestExecutor
from .impl import CommandInspector
from .model.test_result import TestResult


class SodiumInspector:
    """
        SodiumInspector - instantate to inspect a command as it's created, and pull out UI ids that could be testable objects
    """
    def __init__(self):
        self._handler = None
        self._input_ids = {}

    def _make_close_callback(self, cmddef, handler):
        def callback():
            cmddef.commandCreated.remove(handler)
            self.print_results()

        return callback

    def inspect(self, cmdid):
        try:
            app = adsk.core.Application.get()
            userInterface = app.userInterface
            cmddef = userInterface.commandDefinitions.itemById(cmdid)
            if cmddef is None:
                print('Command not found at id ' + cmdid)
            else:
                ids = []
                self._input_ids[cmddef.id] = ids
                self._handler = CommandInspector(ids)
                self._handler.set_close_callback(self._make_close_callback(cmddef, self._handler))
                cmddef.commandCreated.add(self._handler)
                cmddef.execute()
        except:
            traceback.print_exc()


    def print_results(self):
        print('%d commands inspected' % len(self._input_ids))
        print('')
        for k in self._input_ids:
            print('For command id=%s:' % k)
            for cmdid in self._input_ids[k]:
                print(cmdid)
            print('-----------------------')


class SodiumTestRunner(adsk.core.CustomEventHandler):
    """
        SodiumTestRunner - A test runner for CommandTestCase tests.  Use this class by adding all of the tests you want
        to run, and then calling run.
    """
    def __init__(self):
        super().__init__()
        self._testcases = []
        self._complete_handlers = []
        self._results = []
        self._handler = None
        self._event_id = uuid.uuid4().hex

    def _pre_run(self):
        app = adsk.core.Application.get()
        event = app.registerCustomEvent(self._event_id)
        event.add(self)

    def _cleanup(self):
        app = adsk.core.Application.get()
        app.unregisterCustomEvent(self._event_id)

    def add_complete_handler(self, h):
        self._complete_handlers.append(h)

    def add(self, testcase):
        self._testcases.append(testcase)

    def run(self):
        self._pre_run()
        self._run_next()

    def _make_test_finish(self, testcase):
        def finalize(success, exception):
            try:
                testcase.tearDown()
            except:
                pass

            if success:
                self._results.append(TestResult(testcase.name, True, ''))
            else:
                self._results.append(TestResult(testcase.name, False, str(exception)))
        return finalize

    def _run_next(self):
        app = adsk.core.Application.get()
        app.fireCustomEvent(self._event_id)

    def _cleanup_test_and_run_next(self, cmddef, handler):
        cmddef.commandCreated.remove(handler)
        self._run_next()

    def notify(self, args):
        if self._testcases:
            print('Starting test!')
            testcase = self._testcases.pop(0)
            test_finish = self._make_test_finish(testcase)
            cmddef = None
            try:
                cmddef = testcase.setUp()
                # FIXME: this could stand to be cleaned up.  Basically, we create the test executor, add it as a commandCreated
                # handler (which needs to be undone in all cases, success, failure, or exception), set up the executor
                # to run our test, record our results, and run the next test on destroy, and then kick off the test
                # cmddef can be local, but the handler needs a global/long lived reference (hence self._handler)
                # and we need to clean up properly in our exception code as well
                self._handler = CommandTestExecutor(None)
                self._handler.on_test_run(testcase.testCommand)
                self._handler.on_test_finish(test_finish)
                self._handler.on_test_destroy(lambda: self._cleanup_test_and_run_next(cmddef, self._handler))
                cmddef.commandCreated.add(self._handler)
                print('Executing...')
                cmddef.execute()
            except Exception as e:
                traceback.print_exc()
                test_finish(False, e)
                if cmddef is not None and self._handler is not None:
                    self._cleanup_test_and_run_next(cmddef, self._handler)
                else:
                    self._run_next()
        else:
            self._cleanup()
            self._notify_complete()

    def _notify_complete(self):
        for h in self._complete_handlers:
            h(self)

    def print_results(self):
        print('Test results:')
        successes = len([r for r in self._results if r.success])
        for r in self._results:
            print('%s: %s %s' % (r.name, 'SUCCESS' if r.success else 'FAILURE', r.message))
        print('%d of %d tests succeeded.' % (successes, len(self._results)))
