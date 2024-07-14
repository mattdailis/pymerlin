from collections import namedtuple
from queue import Queue, Empty
from threading import Thread

from pymerlin._internal import _globals
from pymerlin._internal._condition import Condition
from pymerlin._internal._context import _set_context, _clear_context
from pymerlin._internal._task_factory import TaskFactory
from pymerlin._internal._task_specification import TaskInstance
from pymerlin._internal._task_status import Completed, Delayed, Awaiting, Calling
from pymerlin.duration import MICROSECONDS

# Host-to-task message types
Resume = namedtuple("Resume", "scheduler")
Abort = namedtuple("Abort", "")

# Task-to-host message types
Yield = namedtuple("Yield", "status")
Aborted = namedtuple("Aborted", "")
Finished = namedtuple("Finished", "value")
Error = namedtuple("Error", "exception")


class ThreadedTaskHost:
    def __init__(self, gateway, model_type, task_provider):
        if type(task_provider) is not TaskInstance:
            raise ValueError(repr(task_provider))
        from pymerlin._internal._model_type import ModelType
        if type(model_type) is not ModelType:
            raise ValueError(repr(model_type))
        self.gateway = gateway
        self.task_thread = _ThreadedTask(task_provider, model_type, gateway)
        self.task_thread_started = False
        self.model_type = model_type

    def step(self, scheduler):
        if not self.task_thread_started:
            self.task_thread.start(scheduler)
            self.task_thread_started = True
        else:
            self.task_thread.inbox.put(Resume(scheduler))
        response = self.task_thread.outbox.get()
        if type(response) is Yield:
            return wrap_status(self.gateway, response.status, self, self.model_type)
        if type(response) is Finished:
            return wrap_status(self.gateway, Completed(response.value), self, self.model_type)
        if type(response) is Aborted:
            raise Exception("Unexpected task abort")
        if type(response) is Error:
            raise response.exception
        else:
            raise Exception("Unhandled task-to-host message type: " + repr(response))

    def release(self):
        self.task_thread.inbox.put(Abort())
        try:
            response = self.task_thread.outbox.get(timeout=5) # Allow task 5 seconds to abort
            if type(response) is not Aborted:
                raise Exception("Task was asked to abort, but instead responded with " + repr(response))
        except Empty as e:
            raise Exception("Task failed to respond to abort request before timeout")

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.Task"]


class _ThreadedTask:
    def __init__(self, task, model_type, gateway):
        self.inbox = Queue(maxsize=1)
        self.outbox = Queue(maxsize=1)
        self.thread = None
        self.task = task
        self.model_type = model_type
        self.aborting = False
        self.gateway = gateway

    def start(self, scheduler):
        self.thread = Thread(target=lambda: self._run(scheduler))
        self.thread.start()

    def _spawn(self, task_provider):
        new_task = ThreadedTaskHost(self.gateway, self.model_type, task_provider)
        _globals._current_context[0].spawn(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.InSpan.Fresh,
                        TaskFactory(lambda: new_task))

    def _run(self, scheduler):
        try:
            _set_context(scheduler, self._spawn, self, self.model_type)
            result = self.task.run()
            self.outbox.put(Finished(result))
        except TaskAbort:
            self.outbox.put(Aborted())
        except Exception as e:
            _clear_context()
            self.outbox.put(Error(e))

    def yield_with(self, status):
        if self.aborting:
            raise TaskAbort()
        _clear_context()
        self.outbox.put(Yield(status))
        request = self.inbox.get()
        if type(request) == Resume:
            _set_context(request.scheduler, self._spawn, self, self.model_type)
            return
        elif type(request) == Abort:
            self.aborting = True
            raise TaskAbort()

class TaskAbort(Exception):
    def __init__(self):
        pass

def wrap_status(gateway, result, continuation, model_type):
    if type(result) == Completed:
        return TaskStatus.completed(gateway, result.value)
    if type(result) == Delayed:
        return TaskStatus.delayed(gateway,
                                  gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.of(
                                      int(result.duration.to_number_in(MICROSECONDS)),
                                      gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECONDS),
                                  continuation)
    if type(result) == Awaiting:
        return TaskStatus.awaiting(gateway, Condition(gateway, result.condition), continuation)
    if type(result) == Calling:
        new_task = ThreadedTaskHost(gateway, model_type, result.child)
        return TaskStatus.calling(gateway, gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.InSpan.Fresh,
                                  TaskFactory(lambda: new_task), continuation)

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
