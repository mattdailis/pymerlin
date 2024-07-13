"""
Provide the MissionModel decorator, which generates the .ActivityType decorators on the decorated class.
"""

import inspect
import warnings
from dataclasses import dataclass


def MissionModel(cls):
    """
    Decorate a class
    :param cls:
    :return:
    """
    if not inspect.isclass(cls):
        warnings.warn("@MissionModel decorator is intended to be used on classes")

    cls.activity_types = {}

    def ActivityType(func):
        activity_definition = wrap(func)
        if activity_definition.name in cls.activity_types:
            warnings.warn("Re-defining activity type: " + activity_definition.name)
        cls.activity_types[activity_definition.name] = activity_definition
        return activity_definition
    cls.ActivityType = ActivityType
    return cls


def Task(func):
    return TaskDefinition(func)


def Validation(validator, message=None):
    def dict_validator(args):
        filtered = {}
        for arg in inspect.getfullargspec(validator).args:
            filtered[arg] = args[arg]
        return ValidationResult(validator(**filtered), message)
    def inner(func):
        activity_definition = wrap(func)
        activity_definition.add_validation(dict_validator)
        return activity_definition
    return inner


@dataclass
class ValidationResult:
    success: bool
    message: str


class TaskDefinition:
    def __init__(self, inner):
        self.inner = inner
        self.name = inner.__name__
        self.validations = []

    def add_validation(self, validation):
        self.validations.insert(0, validation)

    def run_task_definition(self, *args, **kwargs):
        return self.inner.__call__(*args, **kwargs)


def wrap(x):
    """
    This function exists to help @Validation be less order-dependent with @Task and @ActivityType
    """
    if type(x) == TaskDefinition:
        return x
    if callable(x):
        return TaskDefinition(x)
    raise Exception("Unhandled variant: " + str(type(x)))