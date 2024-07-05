from py4j.java_collections import MapConverter, ListConverter, JavaMap, JavaList

def from_serialized_value(gateway, value):
    return value.match(SerializedValueVisitor(gateway))


class SerializedValueVisitor:
    def __init__(self, gateway):
        self.gateway = gateway

    def onNull(self, value):
        return None

    def onNumeric(self, value):
        return float(value)

    def onBoolean(self, value):
        return bool(value)

    def onString(self, value):
        return str(value)

    def onMap(self, value):
        return {k: from_serialized_value(self.gateway, v) for k, v in value.items()}

    def onList(self, value):
        return [from_serialized_value(self.gateway, v) for v in value]

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue$Visitor"]


def to_serialized_value(gateway, value):
    if type(value) is str:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(value)
    if type(value) is int:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(value)
    if type(value) is float:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(value)
    if type(value) is dict or type(value) is JavaMap:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(
            MapConverter().convert({
                k: to_serialized_value(gateway, v) for k, v in value.items()
            }, gateway._gateway_client))
    if type(value) is list or type(value) is JavaList:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(
            ListConverter().convert([
                to_serialized_value(gateway, v) for v in value
            ], gateway._gateway_client))
    raise NotImplementedError(value)