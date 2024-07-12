"""
Provide the MissionModel decorator, which generates the .ActivityType decorators on the decorated class.
"""

import inspect
import warnings
from dataclasses import dataclass

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
        if type(func) == Validatable:
            name = func.inner.__name__
            validations = func.validations
            func = func.inner
        else:
            name = func.__name__
            validations = []
        if name in cls.activity_types:
            warnings.warn("Re-defining activity type: " + func.__name__)
        cls.activity_types[name] = func
        def instantiator(mission=None, **kwargs):
            return TaskSpecification(func, kwargs, mission, validations)
        return instantiator
    cls.ActivityType = ActivityType
    return cls


def Validation(validator, message=None):
    def dict_validator(args):
        filtered = {}
        for arg in inspect.getfullargspec(validator).args:
            filtered[arg] = args[arg]
        return ValidationResult(validator(**filtered), message)
    def inner(func):
        if type(func) == Validatable:
            return Validatable(func.inner, [dict_validator] + func.validations)
        else:
            return Validatable(func, [dict_validator])
    return inner


@dataclass
class ValidationResult:
    success: bool
    message: str


class Validatable:
    def __init__(self, inner, validations):
        self.inner = inner
        self.validations = validations