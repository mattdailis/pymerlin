"""
Provide the MissionModel decorator, which generates the .ActivityType decorators on the decorated class.
"""

import inspect
import warnings

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

    def inner(func):
        if func.__name__ in cls.activity_types:
            warnings.warn("Re-defining activity type: " + func.__name__)
        cls.activity_types[func.__name__] = func
        def innermost(mission=None, **kwargs):
            return TaskSpecification(func, kwargs, mission)
        return innermost
    cls.ActivityType = inner
    return cls