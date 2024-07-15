from contextlib import contextmanager

from pymerlin._internal import _globals


class Registrar:
    def __init__(self):
        self.cells = []
        self.resources = []
        self.topics = []

    def cell(self, initial_value, evolution=None):
        ref = CellRef()
        self.cells.append((ref, initial_value, evolution))
        return ref

    def resource(self, name, f):
        """
        Declare a resource to track
        :param name: The name of the resource
        :param f: A function to calculate the resource, or a cell that contains the value of the resource
        """
        if not callable(f):
            cell = f
            f = cell.get
        self.resources.append((name, f))

    def topic(self, name):
        pass


class Gettable:
    def __init__(self, func):
        self.func = func

    def get(self):
        return self.func()

    def map(self, new_func):
        return Gettable(lambda: new_func(self.get()))

    def __add__(self, other):
        if _is_gettable(other):
            return Gettable(lambda: self.get() + other.get())
        else:
            return Gettable(lambda: self.get() + other)

    def __sub__(self, other):
        if _is_gettable(other):
            return Gettable(lambda: self.get() - other.get())
        else:
            return Gettable(lambda: self.get() - other)

    def __mul__(self, other):
        if _is_gettable(other):
            return Gettable(lambda: self.get() * other.get())
        else:
            return Gettable(lambda: self.get() * other)

    def __div__(self, other):
        if _is_gettable(other):
            return Gettable(lambda: self.get() / other.get())
        else:
            return Gettable(lambda: self.get() / other)

    def __pow__(self, other, modulo=None):
        if _is_gettable(other):
            return Gettable(lambda: self.get() ** other.get())
        else:
            return Gettable(lambda: self.get() ** other)

    def __mod__(self, other):
        if _is_gettable(other):
            return Gettable(lambda: self.get() % other.get())
        else:
            return Gettable(lambda: self.get() % other)

def _is_gettable(obj):
    return callable(getattr(obj, "get", None))

class CellRef(Gettable):
    """
    A reference to an allocated piece of simulation state
    """

    def __init__(self):
        super().__init__(self._get)
        self.id = None
        self.topic = None

    def emit(self, event):
        if not callable(event):
            raise Exception("Expecting effect to be callable")
        _globals.effects_by_id[_globals.next_effect_id] = event
        _globals._current_context[0].emit(_globals.next_effect_id, self.topic)
        _globals.next_effect_id += 1

    def set(self, new_value):
        self.emit(set_value(new_value))

    def add(self, addend):
        self.emit(add_number(addend))

    def _get(self):
        return _globals.cell_values_by_id[_globals._current_context[0].get(self.id)]

    def __iadd__(self, other):
        self.emit(lambda x: x + other)
        return self

    def __isub__(self, other):
        self.emit(lambda x: x - other)
        return self

    def __imul__(self, other):
        self.emit(lambda x: x * other)
        return self

    def __idiv__(self, other):
        self.emit(lambda x: x / other)
        return self

    def __imod__(self, other):
        self.emit(lambda x: x % other)
        return self

def set_value(new_value):
    return lambda x: new_value

@contextmanager
def using(cell_ref, quantity):
    cell_ref += quantity
    yield
    cell_ref -= quantity

# class FunctionalEffect:
#     def __init__(self, f):
#         self.f = f
#
#     def apply(self, state):
#         return self.f(state)
#
#     class Java:
#         implements = ["java.util.function.Function"]


def add_number(addend):
    pass
