from pymerlin._internal._effect_trait import EffectTrait


class CellType:
    def __init__(self, gateway):
        self.gateway = gateway

    def getEffectType(self):
        """

        :return: EffectTrait
        """
        return EffectTrait()

    def duplicate(self, state):
        return self.gateway.jvm.org.apache.commons.lang3.mutable.MutableObject(state.getValue())

    def apply(self, state, effect):
        state.setValue(effect.apply(state.getValue()))

    def step(self, state, duration):
        pass

    def getExpiry(self, state):
        return self.gateway.jvm.java.util.Optional.empty()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.CellType"]