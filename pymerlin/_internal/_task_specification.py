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
