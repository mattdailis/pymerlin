class TaskSpecification:
    def __init__(self, func, kwargs, mission):
        self.func = func
        self.args = kwargs
        self.mission = mission
        # self.kwargs = kwargs

    def instantiate(self):
        if self.mission is None:
            return self.func(**self.args) #, **self.kwargs)
        else:
            return self.func(self.mission, **self.args)  # , **self.kwargs)

    def __repr__(self):
        return f"{self.func.__name__}({self.args}, {self.kwargs})"

    def __call__(self, *args, **kwargs):
        return self.instantiate()
