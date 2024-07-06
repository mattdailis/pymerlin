from pymerlin._internal import _globals
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
        cell_id = _globals.next_cell_id
        _globals.cell_values_by_id[cell_id] = _globals.cell_values_by_id[state]
        _globals.next_cell_id += 1
        return cell_id

    def apply(self, state, effect):
        # TODO pass reference to effect.apply? Do we get a reference back? How expensive is that?
        current_state = _globals.cell_values_by_id[state]
        new_state = effect.apply(current_state)
        _globals.cell_values_by_id[state] = new_state

    def step(self, state, java_duration):
        if self.evolution is None:
            return
        current_state = _globals.cell_values_by_id[state]
        duration = Duration.of(java_duration.dividedBy(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECOND), MICROSECONDS)
        _globals.cell_values_by_id[state] = self.evolution(current_state, duration)

    def getExpiry(self, state):
        return self.gateway.jvm.java.util.Optional.empty()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.CellType"]