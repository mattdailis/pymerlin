import asyncio
import os
from collections import namedtuple
from contextlib import contextmanager

from py4j.java_collections import MapConverter, ListConverter, JavaMap, JavaList

from pymerlin import model_actions
from pymerlin.decorators import TaskSpecification
from pymerlin.duration import Duration, MICROSECONDS
from pymerlin.gateway import start_gateway
from pymerlin.model_actions import Completed, Delayed, Awaiting, Calling
from pymerlin.py4j_utilities import make_array

from py4j.java_gateway import Py4JJavaError, get_field

models_by_id = {}


class CellRef:
    def __init__(self):
        self.id = None
        self.topic = None

    def emit(self, event):
        model_actions._context[0].emit(event, self.topic)

    def get(self):
        return model_actions._context[0].get(self.id).getValue()


class Registrar:
    def __init__(self):
        self.cells = []
        self.resources = []
        self.topics = []

    def cell(self, initial_value):
        ref = CellRef()
        self.cells.append((ref, initial_value))
        return ref

    def resource(self, name, f):
        """
        Declare a resource to track
        :param name: The name of the resource
        :param f: A function to calculate the resource, or a cell that contains the value of the resource
        """
        if not callable(f):
            cell = f
            f = cell.get
        self.resources.append((name, f))

    def topic(self, name):
        pass


class ModelType:
    def __init__(self, model_class):
        self.gateway = None
        self.model_class = model_class
        self.raw_activity_types = model_class.activity_types
        self.activity_types = []

    def set_gateway(self, gateway):
        self.gateway = gateway
        self.activity_types = []
        for activity in self.raw_activity_types.values():
            self.activity_types.append((activity, gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.driver.Topic(),
                                        gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.driver.Topic()))

    def instantiate(self, start_time, config, builder):
        cell_type = CellType(self.gateway)

        registrar = Registrar()
        model = self.model_class(registrar)

        for cell_ref, initial_value in registrar.cells:
            topic = self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.driver.Topic()
            cell_id = builder.allocate(self.gateway.jvm.org.apache.commons.lang3.mutable.MutableObject(initial_value),
                                       cell_type, self.gateway.jvm.java.util.function.Function.identity(), topic)
            cell_ref.id = cell_id
            cell_ref.topic = topic

        for activity, input_topic, output_topic in self.activity_types:
            activity_type_name = activity.__name__
            builder.topic(f"ActivityType.Input.{activity_type_name}", input_topic, OutputType(self.gateway))
            builder.topic(f"ActivityType.Output.{activity_type_name}", output_topic, OutputType(self.gateway))

        for resource_name, resource_func in registrar.resources:
            builder.resource(resource_name, Resource(self.gateway, resource_func))

        models_by_id[id(model)] = model, self
        return id(model)

    def getDirectiveTypes(self):
        return MapConverter().convert(
            {
                activity_type[0].__name__: DirectiveType(
                    self.gateway,
                    activity_type[0],  # function
                    activity_type[1],  # input_topic
                    activity_type[2])  # output_topic
                for activity_type in self.activity_types
            },
            self.gateway._gateway_client)

    def getConfigurationType(self):
        pass

    def toString(self):
        return str(self)

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.ModelType"]


class Resource:
    def __init__(self, gateway, resource_func):
        self.gateway = gateway
        self.func = resource_func

    def getType(self):
        return "discrete"

    def getOutputType(self):
        return OutputType(self.gateway)

    def getDynamics(self, querier):
        with model_actions.context(QuerierAdapter(querier)):
            return self.func()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.Resource"]


class QuerierAdapter:
    def __init__(self, querier):
        self.querier = querier

    def get(self, cell_id):
        return self.querier.getState(cell_id)


class CellType:
    def __init__(self, gateway):
        self.gateway = gateway

    def getEffectType(self):
        """

        :return: EffectTrait
        """
        return EffectTrait()

    def duplicate(self, state):
        return self.gateway.jvm.org.apache.commons.lang3.mutable.MutableObject(state.getValue())

    def apply(self, state, effect):
        state.setValue(effect)

    def step(self, state, duration):
        pass

    def getExpiry(self, state):
        return self.gateway.jvm.java.util.Optional.empty()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.CellType"]


class EffectTrait:
    def empty(self):
        return 0
    def sequentially(self, prefix, suffix):
        return suffix
    def concurrently(self, left, right):
        return 0
    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.EffectTrait"]


class InputType:
    def getParameters(self):
        return []

    def getRequiredParameters(self):
        return []

    def instantiate(self, args):
        return None

    def getArguments(self, val):
        return {}

    def getValidationFailures(self, val):
        return []

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.InputType"]


def to_serialized_value(gateway, value):
    if type(value) is str:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(value)
    if type(value) is int:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(value)
    if type(value) is float:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(value)
    if type(value) is dict or type(value) is JavaMap:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(
            MapConverter().convert({
                k: to_serialized_value(gateway, v) for k, v in value.items()
            }, gateway._gateway_client))
    if type(value) is list or type(value) is JavaList:
        return gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue.of(
            ListConverter().convert([
                to_serialized_value(gateway, v) for v in value
            ], gateway._gateway_client))
    raise NotImplementedError(value)


def from_serialized_value(gateway, value):
    return value.match(SerializedValueVisitor(gateway))


class SerializedValueVisitor:
    def __init__(self, gateway):
        self.gateway = gateway

    def onNull(self, value):
        return None

    def onNumeric(self, value):
        return float(value)

    def onBoolean(self, value):
        return bool(value)

    def onString(self, value):
        return str(value)

    def onMap(self, value):
        return {k: from_serialized_value(self.gateway, v) for k, v in value.items()}

    def onList(self, value):
        return [from_serialized_value(self.gateway, v) for v in value]

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue$Visitor"]


class OutputType:
    def __init__(self, gateway):
        self.gateway = gateway

    def getSchema(self):
        pass  # TODO return ValueSchema

    def serialize(self, value):
        return to_serialized_value(self.gateway, value)

    def hashCode(self):
        return 0

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.OutputType"]


class Consumer:
    def __init__(self, f):
        self.f = f

    def accept(self, args):
        self.f.__call__(args)

    class Java:
        implements = ["java.util.function.Consumer"]


class DirectiveType:
    def __init__(self, gateway, activity, input_topic, output_topic):
        self.gateway = gateway
        self.activity = activity
        self.input_topic = input_topic
        self.output_topic = output_topic

    def getInputType(self):
        return InputType()

    def getOutputType(self):
        return None

    def getTaskFactory(self, model_id, args):
        return TaskFactory(lambda: Task(self.gateway, models_by_id[model_id], self.activity, self.input_topic, self.output_topic))

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.DirectiveType"]


class TaskFactory:
    def __init__(self, task_factory):
        self.task_factory = task_factory

    def create(self, executor):
        return self.task_factory.__call__()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.TaskFactory"]


_future = [None]

async def propagate_exception(f):
    try:
        return await f()
    except Exception as e:
        _future[0].set_exception(e)

class Task:
    def __init__(self, gateway, model, activity, input_topic=None, output_topic=None):
        self.gateway = gateway
        self.model, self.model_type = model
        self.activity = activity
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.continuation = None
        self.task_handle = None
        self.loop = None

    def step(self, scheduler):
        def spawn(child: TaskSpecification):
            new_task = Task(self.gateway, (self.model, self.model_type), child, *get_topics(self.model_type, child.func))
            scheduler.spawn(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.InSpan.Fresh, TaskFactory(lambda: new_task))
        with model_actions.context(scheduler, spawn):
            if self.continuation is None:
                self.loop = asyncio.new_event_loop()
                if self.input_topic is not None:
                    scheduler.emit({}, self.input_topic)
                task_handle, future, done_callback = run_task(self.loop, self.activity, self.model)
                if self.output_topic is not None:
                    scheduler.emit("doesn't matter", self.output_topic)
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
                new_task = Task(self.gateway, (self.model, self.model_type), result.child, *get_topics(self.model_type, result.child.func))
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


def get_topics(model_type: ModelType, func):
    for activity_func, input_topic, output_topic in model_type.activity_types:
        if activity_func is func:
            return input_topic, output_topic
    return None, None




def on_task_finish(future):
    def inner(fut):
        try:
            future.set_result((Completed(fut.result()), "finished"))
        except asyncio.CancelledError:
            pass
        finally:
            model_actions.clear_context()
            model_actions.clear_yield_callback()

    return inner


def on_task_yield(future, task_handle, done_callback):
    def inner(y, continuation):
        try:
            future.set_result((y, continuation))
            task_handle.remove_done_callback(done_callback)
        finally:
            model_actions.clear_context()  # Catch if activity forgets to await
            model_actions.clear_yield_callback()

    return inner


def run_task(loop, task, model):
    future = loop.create_future()
    task_handle = loop.create_task(propagate_exception(lambda: task.__call__(model)))
    done_callback = on_task_finish(future)
    task_handle.add_done_callback(done_callback)
    model_actions.set_yield_callback(on_task_yield(future, task_handle, done_callback))
    return task_handle, future, done_callback


def resume_task(loop, task_handle, continuation):
    future = loop.create_future()
    done_callback = on_task_finish(future)
    task_handle.add_done_callback(done_callback)
    model_actions.set_yield_callback(on_task_yield(future, task_handle, done_callback))
    continuation.set_result("ignored")
    return future


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


class Condition:
    def __init__(self, gateway, func):
        """
        func should return True or False (for now...)
        """
        self.gateway = gateway
        self.func = func

    def nextSatisfied(self, querier, horizon):
        with model_actions.context(QuerierAdapter(querier)):
            if self.func():
                return self.gateway.jvm.java.util.Optional.of(self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.ZERO)
            else:
                return self.gateway.jvm.java.util.Optional.empty()  # Optional<Duration>

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.Condition"]


def make_schedule(gateway, schedule):
    entry_list = []
    for offset, directive in schedule.entries:
        entry_list.append(gateway.jvm.org.apache.commons.lang3.tuple.Pair.of(
            gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECOND.times(offset.micros),
            gateway.jvm.gov.nasa.ammos.aerie.merlin.python.Directive(
                directive.type,
                gateway.jvm.java.util.Map.of())))
    return gateway.jvm.gov.nasa.ammos.aerie.merlin.python.Schedule.build(
        make_array(
            gateway,
            gateway.jvm.org.apache.commons.lang3.tuple.Pair,
            entry_list)
    )


def simulate_helper(gateway, model_type, config, schedule, duration):
    valid_types = set(model_type.getDirectiveTypes().keys())
    for offset, directive in schedule.entries:
        if directive.type not in valid_types:
            raise Exception("Unknown activity type: " + directive.type)
    merlin = gateway.entry_point.getMerlin()
    if type(duration) is str:
        duration = Duration.from_string(duration)
    duration = gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECONDS.times(duration.micros)
    start_time = gateway.jvm.java.time.Instant.EPOCH
    schedule = make_schedule(gateway, schedule)
    return merlin.simulate(model_type, config, schedule, start_time, duration)


def simulate(model_type, schedule, duration):
    if not type(model_type) == ModelType:
        model_type = ModelType(model_type)
    with start_gateway(os.path.join(os.path.dirname(__file__), '../pymerlin.jar')) as gateway:
        try:
            model_type.set_gateway(gateway)
            config = None
            results = simulate_helper(gateway, model_type, config, schedule, duration)
            profiles, spans, events = unpack_simulation_results(gateway, results)
            return profiles, spans, events

        except Py4JJavaError as e:
            e.java_exception.printStackTrace()
            # TODO extract all info from java exception and raise a purely python exception
            raise e


ProfileSegment = namedtuple("ProfileSegment", "extent dynamics")
Span = namedtuple("Span", "type start duration")


def unpack_simulation_results(gateway, results):
    start_time = unix_micros_from_instant(get_field(results, 'startTime'))

    profiles = {}
    for profile_name, profile_segments in get_field(results, 'discreteProfiles').items():
        profiles[profile_name] = [ProfileSegment(
            Duration.of(x.extent().dividedBy(gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECOND),
                        MICROSECONDS),
            from_serialized_value(gateway, x.dynamics())) for x in profile_segments.getRight()]

    spans = []
    for activity_id, activity in get_field(results, 'simulatedActivities').items():
        spans.append(
            Span(activity.type(), Duration.of(unix_micros_from_instant(activity.start()) - start_time, MICROSECONDS),
                 Duration.of(activity.duration().dividedBy(
                     gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECOND), MICROSECONDS)))
    for activity_id, activity in get_field(results, 'unfinishedActivities').items():
        spans.append(
            Span(activity.type(), Duration.of(unix_micros_from_instant(activity.start()) - start_time, MICROSECONDS),
                 None))

    events = []

    return profiles, spans, events


def unix_micros_from_instant(instant):
    seconds = instant.getEpochSecond()
    nanos = instant.getNano()
    return int((seconds * 1_000_000) + (nanos / 1000))