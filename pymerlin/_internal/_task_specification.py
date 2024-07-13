class TaskInstance:
    def __init__(self, func, kwargs, model, validations, definition):
        self.func = func
        self.args = kwargs
        self.model = model
        self.validations = validations  #
        self.definition = definition
        # self.kwargs = kwargs

    def instantiate(self):
        if self.model is None:
            return self.func(**self.args) #, **self.kwargs)
        else:
            return self.func(self.model, **self.args)  # , **self.kwargs)

    def validate(self):
        return [
            validation(self.args)
            for validation in self.validations
        ]

    def __repr__(self):
        return f"{self.definition.name}({', '.join(f'{k}={v}' for k, v in self.args.items())})"

    def __call__(self, *args, **kwargs):
        return self.instantiate()
