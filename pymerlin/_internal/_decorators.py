"""
Provide the MissionModel decorator, which generates the .ActivityType decorators on the decorated class.
"""

import inspect
import warnings
from dataclasses import dataclass

from pymerlin._internal._execution_mode import TaskExecutionMode
from pymerlin._internal._task_specification import TaskSpecification


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
        activity_definition = wrap(func, "ACTIVITY")
        if activity_definition.name in cls.activity_types:
            warnings.warn("Re-defining activity type: " + activity_definition.name)
        cls.activity_types[activity_definition.name] = activity_definition
        def instantiator(mission=None, **kwargs):
            return TaskSpecification(func, kwargs, mission, activity_definition.validations, activity_definition)
        return instantiator
    cls.ActivityType = ActivityType
    return cls


def Task(func):
    activity_definition = wrap(func, "TASK")
    def instantiator(mission=None, **kwargs):
        return TaskSpecification(func, kwargs, mission, activity_definition.validations, activity_definition)
    return instantiator


def Validation(validator, message=None):
    def dict_validator(args):
        filtered = {}
        for arg in inspect.getfullargspec(validator).args:
            filtered[arg] = args[arg]
        return ValidationResult(validator(**filtered), message)
    def inner(func):
        activity_definition = wrap(func, "ACTIVITY")
        activity_definition.add_validation(dict_validator)
        return activity_definition
    return inner


@dataclass
class ValidationResult:
    success: bool
    message: str


class ActivityDefinition:
    def __init__(self, inner, execution_mode, type):
        self.inner = inner
        self.name = inner.__name__
        self.validations = []
        self.execution_mode = execution_mode
        self.type = type

    def add_validation(self, validation):
        self.validations.insert(0, validation)

    def __call__(self, *args, **kwargs):
        return self.inner.__call__(*args, **kwargs)


def wrap(x, task_type):
    if type(x) == ActivityDefinition:
        return x
    if inspect.iscoroutinefunction(x):
        return ActivityDefinition(x, TaskExecutionMode.ASYNC, task_type)
    if callable(x):
        return ActivityDefinition(x, TaskExecutionMode.THREADED, task_type)
    raise Exception("Unhandled variant: " + str(type(x)))