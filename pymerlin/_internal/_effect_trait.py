from pymerlin._internal import _globals


class EffectTrait:
    def empty(self):
        return 0
    def sequentially(self, prefix, suffix):
        return suffix
    def concurrently(self, left_id, right_id):
        def try_both(x):
            left = _globals.effects_by_id[left_id]
            right = _globals.effects_by_id[right_id]
            res1 = left(right(x))
            res2 = right(left(x))
            if res1 != res2:
                raise Exception("Concurrent composition of non-commutative effects")
            return res1
        effect_id = _globals.next_effect_id
        _globals.effects_by_id[effect_id] = try_both
        _globals.next_effect_id += 1
        return effect_id
    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.EffectTrait"]
