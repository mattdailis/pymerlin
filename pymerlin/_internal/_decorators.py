"""
Provide the MissionModel decorator, which generates the .ActivityType decorators on the decorated class.
"""

import inspect
import warnings
from dataclasses import dataclass

from pymerlin._internal._serialized_value import from_map_str_serialized_value
from pymerlin._internal._spawn_helpers import activity_wrapper, get_topics
from pymerlin._internal._task_specification import TaskInstance


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
        if type(func) == TaskDefinition:
            activity_definition = func
        elif callable(func):
            activity_definition = TaskDefinition(func.__name__, lambda *args, **kwargs: activity_wrapper(TaskDefinition("inner", func), args, kwargs, *get_topics(activity_definition)))
        else:
            raise ValueError("Cannot decorate " + repr(func) + " with @ActivityType")
        if activity_definition.name in cls.activity_types:
            warnings.warn("Re-defining activity type: " + activity_definition.name)
        cls.activity_types[activity_definition.name] = activity_definition
        return activity_definition
    cls.ActivityType = ActivityType
    return cls


def Task(func):
    return TaskDefinition(func.__name__, func)


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
    """
    TaskDefinition can produce a TaskInstance given all of the arguments for that task
    """
    def __init__(self, name, func):
        self.name = name
        self.inner = func
        self.validations = []

    def add_validation(self, validation):
        self.validations.insert(0, validation)

    def __call__(self, *args, **kwargs):
        return self.make_instance(*args, **kwargs)

    def make_instance(self, *args, **kwargs) -> TaskInstance:
        # inspect.getfullargspec(self.inner)
        # return self.inner.__call__(*args, **kwargs)
        return TaskInstance(lambda: self.inner.__call__(*args, **kwargs))
        # , f"{self.name}({', '.join(f'{k}={v}' for k, v in kwargs.items())})"

    def get_task_factory(self, model, args, gateway, model_type):
        from pymerlin._internal._task_factory import TaskFactory
        from pymerlin._internal._threaded_task import ThreadedTaskHost

        # It is expected that the first argument to an activity be the mission model
        return TaskFactory(lambda: ThreadedTaskHost(gateway, model_type, self.make_instance(model, **from_map_str_serialized_value(gateway, args))))


def wrap(x):
    """
    This function exists to help @Validation be less order-dependent with @Task and @ActivityType
    """
    if type(x) == TaskDefinition:
        return x
    if callable(x):
        return TaskDefinition(x.__name__, x)
    raise Exception("Unhandled variant: " + str(type(x)))