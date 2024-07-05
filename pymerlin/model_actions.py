"""
This module provides actions that tasks can take. Certain actions are labeled `async`, which means they must be called
with the `await` keyword - for example, `await delay("01:00:00")`
"""


import asyncio

from pymerlin._internal._task_status import Delayed, Calling, Awaiting
from pymerlin.duration import Duration
from pymerlin._internal._globals import _current_context, _yield_callback

async def delay(duration):
    if type(duration) is str:
        duration = Duration.from_string(duration)
    elif type(duration) is not Duration:
        raise Exception("Argument to delay must be a Duration or a string representing a duration")
    return await _yield_with(Delayed(duration))


def spawn(child):
    """
    :param coro:
    :return:
    """
    _current_context[1](child)



async def call(child):
    return await _yield_with(Calling(child))


async def wait_until(condition):
    """
    :param condition: A function returning True or False
    """
    return await _yield_with(Awaiting(condition))


async def _yield_with(status):
    loop = asyncio.get_running_loop()
    loop.set_debug(True)
    future = loop.create_future()
    _yield_callback[0].__call__(status, future)

    return await future