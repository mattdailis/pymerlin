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


class CellRef:
    """
    A reference to an allocated piece of simulation state
    """

    def __init__(self):
        self.id = None
        self.topic = None

    def emit(self, event):
        if callable(event):
            event = FunctionalEffect(event)
        _globals._current_context[0].emit(event, self.topic)

    def set_value(self, new_value):
        self.emit(set_value(new_value))

    def add(self, addend):
        self.emit(add_number(addend))

    def get(self):
        return _globals._current_context[0].get(self.id).getValue()


class set_value:
    def __init__(self, new_value):
        # def apply(cell):
        #     return new_value
        self.new_value = new_value

    def apply(self, state):
        return self.new_value

    class Java:
        implements = ["java.util.function.Function"]


class FunctionalEffect:
    def __init__(self, f):
        self.f = f

    def apply(self, state):
        return self.f(state)

    class Java:
        implements = ["java.util.function.Function"]


def add_number(addend):
    pass
