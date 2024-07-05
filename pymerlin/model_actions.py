"""
This module provides actions that tasks can take. Certain actions are labeled `async`, which means they must be called
with the `await` keyword - for example, `await delay("01:00:00")`
"""

import asyncio

import pymerlin._internal._task_status
import pymerlin.duration
import pymerlin._internal._globals


async def delay(duration):
    if type(duration) is str:
        duration = pymerlin.duration.Duration.from_string(duration)
    elif type(duration) is not pymerlin.duration.Duration:
        raise Exception("Argument to delay must be a Duration or a string representing a duration")
    return await _yield_with(pymerlin._internal._task_status.Delayed(duration))


def spawn(child):
    """
    :param coro:
    :return:
    """
    pymerlin._internal._globals._current_context[1](child)


async def call(child):
    return await _yield_with(pymerlin._internal._task_status.Calling(child))


async def wait_until(condition):
    """
    :param condition: A function returning True or False
    """
    return await _yield_with(pymerlin._internal._task_status.Awaiting(condition))


async def _yield_with(status):
    loop = asyncio.get_running_loop()
    loop.set_debug(True)
    future = loop.create_future()
    pymerlin._internal._globals._yield_callback[0].__call__(status, future)

    return await future
