class InputType:
    def getParameters(self):
        return []

    def getRequiredParameters(self):
        return []

    def instantiate(self, args):
        return None

    def getArguments(self, val):
        return {}

    def getValidationFailures(self, val):
        return []

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.InputType"]
