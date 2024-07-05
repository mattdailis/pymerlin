from pymerlin._internal._effect_trait import EffectTrait
from pymerlin.duration import Duration, MICROSECONDS


class CellType:
    def __init__(self, gateway, evolution=None):
        self.gateway = gateway
        self.evolution = evolution

    def getEffectType(self):
        """

        :return: EffectTrait
        """
        return EffectTrait()

    def duplicate(self, state):
        return self.gateway.jvm.org.apache.commons.lang3.mutable.MutableObject(state.getValue())

    def apply(self, state, effect):
        state.setValue(effect.apply(state.getValue()))

    def step(self, state, java_duration):
        if self.evolution is None:
            return
        duration = Duration.of(java_duration.dividedBy(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECOND), MICROSECONDS)
        state.setValue(self.evolution(state.getValue(), duration))

    def getExpiry(self, state):
        return self.gateway.jvm.java.util.Optional.empty()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.CellType"]