import warnings

def MissionModel(cls):
    cls.activity_types = {}

    def inner(func):
        if func.__name__ in cls.activity_types:
            warnings.warn("Re-defining activity type: " + func.__name__)
        cls.activity_types[func.__name__] = func
        def inner(*args, **kwargs):
            return TaskSpecification(func, args, kwargs)
        return inner
    cls.ActivityType = inner
    return cls

class TaskSpecification:
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def instantiate(self):
        return self.func(*self.args, **self.kwargs)

    def __repr__(self):
        return f"{self.func.__name__}({self.args}, {self.kwargs})"

    def __call__(self, *args, **kwargs):
        return self.instantiate()