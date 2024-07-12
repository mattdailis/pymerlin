import os
import warnings
from collections import namedtuple

from py4j.java_gateway import Py4JJavaError, get_field

from pymerlin._internal import _globals
from pymerlin._internal._gateway import start_gateway
from pymerlin._internal._model_type import ModelType
from pymerlin._internal._py4j_utilities import make_array
from pymerlin._internal._schedule import Directive
from pymerlin._internal._serialized_value import from_serialized_value, to_map_str_serialized_value
from pymerlin._internal._task_specification import TaskSpecification
from pymerlin.duration import Duration, MICROSECONDS


class Consumer:
    def __init__(self, f):
        self.f = f

    def accept(self, args):
        self.f.__call__(args)

    class Java:
        implements = ["java.util.function.Consumer"]


def make_schedule(gateway, schedule):
    entry_list = []
    for offset, directive in schedule.entries:
        if type(directive) == TaskSpecification:
            x: TaskSpecification = directive
            directive = Directive(x.func.__name__, x.args)
        entry_list.append(gateway.jvm.org.apache.commons.lang3.tuple.Pair.of(
            gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECOND.times(offset.micros),
            gateway.jvm.gov.nasa.ammos.aerie.merlin.python.Directive(
                directive.type,
                to_map_str_serialized_value(gateway, directive.args))))
    return gateway.jvm.gov.nasa.ammos.aerie.merlin.python.Schedule.build(
        make_array(
            gateway,
            gateway.jvm.org.apache.commons.lang3.tuple.Pair,
            entry_list)
    )


def simulate_helper(gateway, model_type, config, schedule, duration):
    valid_types = set(model_type.getDirectiveTypes().keys())
    for offset, directive in schedule.entries:
        type_name = directive.type if type(directive) == Directive else directive.func.__name__
        if type_name not in valid_types:
            raise Exception("Unknown activity type: " + type_name)
    merlin = gateway.entry_point.getMerlin()
    if type(duration) is str:
        duration = Duration.from_string(duration)
    duration = gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.types.Duration.MICROSECONDS.times(duration.micros)
    start_time = gateway.jvm.java.time.Instant.EPOCH
    schedule = make_schedule(gateway, schedule)
    return merlin.simulate(model_type, config, schedule, start_time, duration)


def simulate(model_type, schedule, duration):
    for _, directive in schedule.entries:
        if type(directive) == TaskSpecification:
            for result in directive.validate():
                if not result.success:
                    warnings.warn(repr(directive) + " failed validation: " + result.message)

    if not type(model_type) == ModelType:
        model_type = ModelType(model_type)
    jar_path = os.path.join(os.path.dirname(__file__), "jars", "pymerlin.jar")
    with start_gateway(jar_path) as gateway:
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

        finally:
            # If we haven't run out of memory from this data structure yet, now's a good time to empty it
            _globals.cell_values_by_id.clear()


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