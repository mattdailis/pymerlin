models_by_id = {}

_current_context = [None, None, None]

next_cell_id = 0

# This is a workaround to be able to recover the original python object after it's gone on a round trip through Java.
# Instead of sending the python object, we send a numeric identifier, which is really a reference to this dictionary.
# TODO figure out when we can clear this dictionary. As written it's a memory leak
# TODO consider allowing mutable objects in this dictionary, for performance purposes. This would require a way to clone these objects
cell_values_by_id = {}

# Consider deduplication, since effects should be immutable
effects_by_id = {}
effects_by_id[0] = lambda x: x
next_effect_id = 1

reaction_context = None
