import asyncio
from collections import namedtuple
from contextlib import contextmanager

from pymerlin.duration import Duration

_context = [None, None]
_yield_callback = []


Completed = namedtuple("Completed", "value")
Delayed = namedtuple("Delayed", "duration")
Calling = namedtuple("Calling", "child")
Awaiting = namedtuple("Awaiting", "condition")


@contextmanager
def context(scheduler, spawner=None):
    set_context(scheduler, spawner)
    yield
    clear_context()


def set_context(context, spawner):
    _context.clear()
    _context.append(context)
    _context.append(spawner)


def clear_context():
    _context.clear()
    _context.append(None)
    _context.append(None)

def set_yield_callback(callback):
    _yield_callback.clear()
    _yield_callback.append(callback)


def clear_yield_callback():
    _yield_callback.clear()
    _yield_callback.append(None)


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
    _context[1](child)



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