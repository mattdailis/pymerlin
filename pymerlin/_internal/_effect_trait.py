class EffectTrait:
    def empty(self):
        return 0
    def sequentially(self, prefix, suffix):
        return suffix
    def concurrently(self, left, right):
        return 0
    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.EffectTrait"]
