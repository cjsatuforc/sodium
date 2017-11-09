
import adsk.core

from .model.test_result import TestResult
from .command_test_executor import CommandTestExecutor
import traceback
import uuid


class SodiumTestRunner(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()
        self._testcases = []
        self._results = []
        self._handler = None
        self._event_id = uuid.uuid4().hex

    def prerun(self):
        app = adsk.core.Application.get()
        event = app.registerCustomEvent(self._event_id)
        event.add(self)

    def cleanup(self):
        app = adsk.core.Application.get()
        app.unregisterCustomEvent(self._event_id)

    def add(self, testcase):
        self._testcases.append(testcase)

    def run(self):
        self.prerun()
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

    def notify(self, args):
        if self._testcases:
            print('Starting test!')
            testcase = self._testcases.pop(0)
            test_finish = self._make_test_finish(testcase)
            try:
                cmddef, base_handler = testcase.setUp()
                self._handler = CommandTestExecutor(base_handler)
                self._handler.on_test_run(testcase.testCommand)
                self._handler.on_test_finish(test_finish)
                self._handler.on_test_destroy(self._run_next)
                cmddef.commandCreated.add(self._handler)
                print('Executing...')
                cmddef.execute()
            except Exception as e:
                traceback.print_exc()
                test_finish(False, e)
                self._run_next()
        else:
            self.print_results()
            self.cleanup()

    def print_results(self):
        print('Test results:')
        successes = len([r for r in self._results if r.success])
        for r in self._results:
            print('%s: %s %s' % (r.name, 'SUCCESS' if r.success else 'FAILURE', r.message))
        print('%d of %d tests succeeded.' % (successes, len(self._results)))
