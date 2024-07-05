from pymerlin import model_actions
from pymerlin._internal._querier_adapter import QuerierAdapter


class Condition:
    def __init__(self, gateway, func):
        """
        func should return True or False (for now...)
        """
        self.gateway = gateway
        self.func = func

    def nextSatisfied(self, querier, horizon):
        with model_actions._context(QuerierAdapter(querier)):
            if self.func():
                return self.gateway.jvm.java.util.Optional.of(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.ZERO)
            else:
                return self.gateway.jvm.java.util.Optional.empty()  # Optional<Duration>

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.Condition"]
