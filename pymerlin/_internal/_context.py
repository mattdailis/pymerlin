from contextlib import contextmanager

from pymerlin._internal._globals import _current_context, _yield_callback


@contextmanager
def _context(scheduler, spawner=None):
    _set_context(scheduler, spawner)
    yield
    _clear_context()


def _set_context(context, spawner):
    _current_context.clear()
    _current_context.append(context)
    _current_context.append(spawner)


def _clear_context():
    _current_context.clear()
    _current_context.append(None)
    _current_context.append(None)

def _set_yield_callback(callback):
    _yield_callback.clear()
    _yield_callback.append(callback)


def _clear_yield_callback():
    _yield_callback.clear()
    _yield_callback.append(None)
