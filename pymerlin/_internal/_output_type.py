from pymerlin._internal._serialized_value import to_serialized_value


class OutputType:
    def __init__(self, gateway):
        self.gateway = gateway

    def getSchema(self):
        pass  # TODO return ValueSchema

    def serialize(self, value):
        return to_serialized_value(self.gateway, value)

    def hashCode(self):
        return 0

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.OutputType"]
