# sodium
Fusion 360 add-in UI testing framework, written in Python.

This framework allows you to automate UI and integration testing for your add-in, running right in Fusion 360.  Though it is written in Python, it should work with add-ins defined in any language (provided to you use our suggested setup).

## Usage

To setup for use (suggested):

* Clone this repository

* Create a new Fusion 360 Add-In to hold your tests

* Create a lib folder inside your test add-in source folder

* Link or copy the sodium folder into your lib folder


To create and run a test:

* Create a file in your test add-in to house your tests, e.g. foo_integration_tests.py
* Add an import statement in that file using relative imports, e.g. "from .lib import sodium"
* Add a class to describe your new testcase.  This class should extend sodium.CommandTestCase,
e.g.
```
    class ExampleTestCase(sodium.CommandTestCase):
    
        def __init__(self):
            super().__init__('Example') # Set the name, used when reporting results
            self._document = None

        def setUp(self):

            # Set up your test fixtures here

            cmdid = ... # Specify the id of the command under test

            app = adsk.core.Application.get()
            cmddef = app.userInterface.commandDefinitions.itemById(cmdid)
            return cmddef

        def testCommand(self, command, inputs):

            # Test the command here.  Inputs is a dict of ids and CommandInput objects,
            # so you can manipulate the value, then execute the command, then test the results

            pass

        def tearDown(self):
            # Tear down your fixtures.  These lines are used to terminate the running command.
            # Note that if your command is set to execute when preempted, this will also execute
            # your command.  You can adjust this on the command object in testCommand by setting
            # command.isExecutedWhenPreEmpted = False

            app = adsk.core.Application.get()
            app.userInterface.commandDefinitions.itemById('SelectCommand').execute()
```
* Add a global test runner instance (making this global will ensure all of the necessary references are held properly):
        
    `runner = sodium.SodiumTestRunner()`

* Add a function to use the runner, add the tests, and run.  This also adds the print_results function as a completion handler,
    so the test results are printed when the runner is finished:
```
    def run_tests():
        global runner
        runner.add(ExampleTestCase())
        runner.add_completion_handler(sodium.SodiumTestRunner.print_results)
        runner.run()
```
* Call run_tests from your Add-in run function

* Use the console in Spyder or the TextCommandPalette in Fusion 360 to view the results.

You can add as many additional tests to your test add-in project, organize your tests into packages, or break out different run_tests functions for different scenarios.

## Questions and Answers

Q: Do I have to create a separate project?

A: No, but it makes things easier, especially since there isn't a tight coupling with the code under test.  Additionally, linking this into your main add-in may have licensing implications.  See the next question for more on this.

Q: Why is this licensed GPLv3?  Will I be able to use it in my commercial application?

A: GPLv3 requires disclosure of source when the including software is distributed, but since all the action happens in a This is GPLv3 because I want to encourage open collaboration and shared responsibility for our tools, but I'm not trying to stop anyone from developing commercial software.  Because you can run your tests from a tests project, you can avoid pulling GPLv3 code into your main project.  I think that, unless you were planning to publish object code of your testing projects without the backing source code, this should have no affect on your commercial application. (I am not a lawyer, this is not legal advice, definitely consult a real opinion if you are concerned about this).

Q: Would you consider changing the license to (fill in the blank)?

A: Maybe.  Open an issue, and in the body, explain the benefits of the new license.  We'll consider it.

Q: How do I report a bug or feature request?

A: Open an issue on this project, and we will review.
 
Q: Are you accepting pull requests?

A: Yes!  We don't have formal guidelines for pull requests yet, but if you have a change you think should be included or a bug you wanted to fix, fork the code, implement the change, and submit the request.  Please note, depending on the change itself, and how our processes evolve, we may ask you to sign a copyright assignment agreement before we can accept your request into this project.

Q: I have more questions.  Can I contact you?

A: Sure!  Please email your questions to me at jesse at bommer.io.

Q: I love what you're doing, and I want to work with you.  Are you hiring?

A: We're always looking for talented people who share our passions, but we are a very early stage startup company, and are not hiring for paid positions right now.  If you're still interested in exploring opportunities, send me a note at the aforementioned address and lets talk!

Q: Why is this named sodium?

A: Because it enables fusion tests (See https://en.wikipedia.org/wiki/Sodium_fusion_test)
