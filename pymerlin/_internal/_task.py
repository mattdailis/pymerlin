import asyncio
from typing import Coroutine

from pymerlin._internal import _globals
from pymerlin._internal._condition import Condition
from pymerlin._internal._context import _context, _set_yield_callback, _clear_context, _clear_yield_callback
from pymerlin._internal._serialized_value import from_map_str_serialized_value
from pymerlin._internal._task_factory import TaskFactory
from pymerlin._internal._task_specification import TaskSpecification

from pymerlin._internal._globals import _future
from pymerlin._internal._task_status import Completed, Delayed, Awaiting, Calling


class Task:
    def __init__(self, gateway, model_type, task_provider):
        self.gateway = gateway
        self.model_type = model_type
        self.continuation = None
        self.task_handle = None
        self.loop = None
        self.task_provider = task_provider

    def step(self, scheduler):
        def spawn(task_provider):
            new_task = Task(self.gateway, self.model_type, task_provider)
            scheduler.spawn(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.InSpan.Fresh,
                            TaskFactory(lambda: new_task))
        with _context(scheduler, spawn):
            if self.continuation is None:
                self.loop = asyncio.new_event_loop()
                task_handle, future, done_callback = run_task(self.loop, self.task_provider)
                self.task_handle = task_handle

            else:
                future = resume_task(self.loop, self.task_handle, self.continuation)
            _future[0] = future
            self.loop.run_until_complete(future)
            result, continuation = future.result()
            self.continuation = continuation

            if type(result) == Completed:
                return TaskStatus.completed(self.gateway, result.value)
            if type(result) == Delayed:
                return TaskStatus.delayed(self.gateway,
                                          self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.of(
                                              result.duration.micros,
                                              self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECONDS),
                                          self)
            if type(result) == Awaiting:
                return TaskStatus.awaiting(self.gateway, Condition(self.gateway, result.condition), self)
            if type(result) == Calling:
                new_task = Task(self.gateway, self.model_type, result.child)
                return TaskStatus.calling(self.gateway, self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.InSpan.Fresh,
                                          TaskFactory(lambda: new_task), self)
            raise Exception("Invalid response from task")

    def release(self):
        if self.loop is not None:
            self.task_handle.cancel()
            self.loop.run_until_complete(self.exit())

    async def exit(self):
        self.loop.stop()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.Task"]


def run_task(loop, task_provider):
    future = loop.create_future()
    task_handle = loop.create_task(propagate_exception(task_provider))
    done_callback = on_task_finish(future)
    task_handle.add_done_callback(done_callback)
    _set_yield_callback(on_task_yield(future, task_handle, done_callback))
    return task_handle, future, done_callback


def resume_task(loop, task_handle, continuation):
    future = loop.create_future()
    done_callback = on_task_finish(future)
    task_handle.add_done_callback(done_callback)
    _set_yield_callback(on_task_yield(future, task_handle, done_callback))
    continuation.set_result("ignored")
    return future


def on_task_finish(future):
    def inner(fut):
        try:
            future.set_result((Completed(fut.result()), "finished"))
        except asyncio.CancelledError:
            pass
        finally:
            _clear_context()
            _clear_yield_callback()

    return inner


def on_task_yield(future, task_handle, done_callback):
    def inner(y, continuation):
        try:
            future.set_result((y, continuation))
            task_handle.remove_done_callback(done_callback)
        finally:
            _clear_context()  # Catch if activity forgets to await
            _clear_yield_callback()

    return inner



class TaskStatus:
    @staticmethod
    def completed(gateway, value):
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.TaskStatus.completed(value)

    @staticmethod
    def delayed(gateway, duration, continuation):
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.TaskStatus.delayed(duration, continuation)

    @staticmethod
    def calling(gateway, child_span, child, continuation):
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.TaskStatus.calling(child_span, child, continuation)

    @staticmethod
    def awaiting(gateway, condition: "Condition", continuation):
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.TaskStatus.awaiting(condition, continuation)


async def propagate_exception(f):
    try:
        return await f()
    except Exception as e:
        _future[0].set_exception(e)