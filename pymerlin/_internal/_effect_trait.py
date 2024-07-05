from pymerlin._internal._registrar import FunctionalEffect


class EffectTrait:
    def empty(self):
        return FunctionalEffect(lambda x: x)
    def sequentially(self, prefix, suffix):
        return suffix
    def concurrently(self, left, right):
        def try_both(x):
            res1 = left.apply(right.apply(x))
            res2 = right.apply(left.apply(x))
            if res1 != res2:
                raise Exception("Concurrent composition of non-commutative effects")
            return res1
        return FunctionalEffect(try_both)
    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.EffectTrait"]
