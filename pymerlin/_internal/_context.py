from contextlib import contextmanager

from pymerlin._internal import _globals
from pymerlin._internal._globals import _current_context


@contextmanager
def _context(scheduler, spawner=None, reaction_context=None):
    _set_context(scheduler, spawner, reaction_context)
    yield
    _clear_context()


def _set_context(context, spawner, reaction_context):
    _current_context.clear()
    _current_context.append(context)
    _current_context.append(spawner)
    _globals.reaction_context = reaction_context


def _clear_context():
    _current_context.clear()
    _current_context.append(None)
    _current_context.append(None)
    _globals.reaction_context = None
