class TaskSpecification:
    def __init__(self, func, kwargs, mission, validations):
        self.func = func
        self.args = kwargs
        self.mission = mission
        self.validations = validations  #
        # self.kwargs = kwargs

    def instantiate(self):
        if self.mission is None:
            return self.func(**self.args) #, **self.kwargs)
        else:
            return self.func(self.mission, **self.args)  # , **self.kwargs)

    def validate(self):
        return [
            validation(self.args)
            for validation in self.validations
        ]

    def __repr__(self):
        return f"{self.func.__name__}({', '.join(f'{k}={v}' for k, v in self.args.items())})"

    def __call__(self, *args, **kwargs):
        return self.instantiate()
