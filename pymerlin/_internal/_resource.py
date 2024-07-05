from pymerlin._internal._context import _context
from pymerlin._internal._output_type import OutputType
from pymerlin._internal._querier_adapter import QuerierAdapter


class Resource:
    def __init__(self, gateway, resource_func):
        self.gateway = gateway
        self.func = resource_func

    def getType(self):
        return "discrete"

    def getOutputType(self):
        return OutputType(self.gateway)

    def getDynamics(self, querier):
        with _context(QuerierAdapter(querier)):
            return self.func()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.Resource"]
