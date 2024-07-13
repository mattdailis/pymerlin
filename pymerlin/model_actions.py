"""
This module provides actions that tasks can take. Certain actions are labeled `async`, which means they must be called
with the `await` keyword - for example, `await delay("01:00:00")`
"""

import pymerlin._internal._task_status
import pymerlin.duration
import pymerlin._internal._globals
from pymerlin._internal._decorators import TaskDefinition
from pymerlin._internal._spawn_helpers import activity_wrapper, get_topics


def delay(duration):
    if type(duration) is str:
        duration = pymerlin.duration.Duration.from_string(duration)
    elif type(duration) is not pymerlin.duration.Duration:
        raise Exception("Argument to delay must be a Duration or a string representing a duration")
    return _yield_with(pymerlin._internal._task_status.Delayed(duration))


def spawn_activity(model, child, args):
    """
    :param coro:
    :return:
    """
    topics = get_topics(model._model_type, child)
    task_provider = TaskDefinition(lambda: activity_wrapper(
        child,
        args,
        model,
        *topics))
    pymerlin._internal._globals._current_context[1](task_provider)


def spawn_task(child, args):
    """
    :param coro:
    :return:
    """
    pymerlin._internal._globals._current_context[1](TaskDefinition(lambda: child.run_task_definition(**args)))


def call(model, child, args):
    if type(child) is not TaskDefinition:
        raise ValueError("Should be TaskDefinition, was: " + repr(child))
    task_provider = TaskDefinition(lambda: activity_wrapper(
        child,
        args,
        model,
        *get_topics(model._model_type, child)))
    return _yield_with(pymerlin._internal._task_status.Calling(task_provider))


def wait_until(condition):
    """
    :param condition: A function returning True or False
    """
    return _yield_with(pymerlin._internal._task_status.Awaiting(condition))


def _yield_with(status):
    return pymerlin._internal._globals.reaction_context.yield_with(status)
