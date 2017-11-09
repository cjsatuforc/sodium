
class CommandTestCase:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def testCommand(self, command, inputs):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
