import pytest
from py4j.java_gateway import Py4JJavaError

from pymerlin import MissionModel
from pymerlin import Schedule
from pymerlin import simulate, Span
from pymerlin._internal._decorators import Validation, ValidationResult
from pymerlin._internal._registrar import Registrar
from pymerlin.duration import Duration, SECONDS
from pymerlin.model_actions import delay, spawn, call, wait_until


@MissionModel
class TestMissionModel:
    def __init__(self, registrar: Registrar):
        self.list = registrar.cell([])
        self.counter = registrar.cell(0)
        self.linear = registrar.cell((0, 1), evolution=linear_evolution)


def linear_evolution(x, d):
    initial = x[0]
    rate = x[1]
    delta = rate * d.micros / 1_000_000
    return initial + delta, rate


@TestMissionModel.ActivityType
async def noop(mission):
    pass


@TestMissionModel.ActivityType
async def add_to_list(mission, item):
    mission.counter.set(mission.counter.get() + 1)
    mission.list.emit(mission.list.get() + [item])


@TestMissionModel.ActivityType
async def delay_one_hour(mission):
    mission.counter.set(mission.counter.get() + 1)
    await delay("01:00:00")


@TestMissionModel.ActivityType
async def clear_list(mission, item):
    mission.counter.set(mission.counter.get() + 1)
    mission.list.emit([])


def test_checkout():
    from pymerlin import checkout
    checkout()


def test_empty():
    """
    Empty schedule should result in no spans
    """
    profiles, spans, events = simulate(TestMissionModel, Schedule.empty(), "24:00:00")
    assert 0 == len(spans)


def test_noop():
    """
    Schedule with noop should have a single span, and all profiles should have exactly one segment
    """
    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:01", noop())), "24:00:00")
    assert spans == [Span("noop", Duration.from_string("00:00:01"), Duration.ZERO)]


def test_effect():
    """
    Make sure the counter gets incremented when expected by observing it from another activity
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        await delay("00:00:00")
        assert mission.counter.get() == 0
        await delay("00:05:00")
        assert mission.counter.get() == 1
        return

    simulate(TestMissionModel,
             Schedule.build(("00:00:00", activity()), ("00:00:01", delay_one_hour())), "24:00:00")


def test_exception():
    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        await delay("00:00:00")
        raise Exception("Exception in task!")

    with pytest.raises(Py4JJavaError) as e:
        simulate(TestMissionModel, Schedule.build(("00:00:00", activity())), "24:00:00")
        # TODO make sure ample information is extracted from the java exception


@pytest.mark.skip("This test hangs, but it would be nice if it raised an exception instead")
def test_forgot_to_await():
    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        delay("00:00:01")
        delay("00:00:01")

    with pytest.raises(Py4JJavaError) as e:
        simulate(TestMissionModel, Schedule.build(("00:00:00", activity())), "24:00:00")
        # TODO make sure ample information is extracted from the java exception


def test_spawn_activity():
    """
    Check that spawning a child activity creates the correct spans, and that concurrent events become visible after yield
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.set(123)
        spawn(mission, other_activity(mission=mission))
        mission.counter.set(345)
        assert mission.counter.get() == 345

    @TestMissionModel.ActivityType
    async def other_activity(mission: TestMissionModel):
        assert mission.counter.get() == 123
        await delay("00:00:01")
        assert mission.counter.get() == 345

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", activity())),
                                       "24:00:00")
    assert spans == [Span("activity", Duration.ZERO, Duration.SECOND),
                     Span("other_activity", Duration.ZERO, Duration.SECOND)]


def test_spawn_task():
    """
    Check that spawning a child task creates no new spans, and that concurrent events become visible after yield
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.set(123)
        spawn(None, subtask(mission=mission))
        mission.counter.set(345)
        assert mission.counter.get() == 345
        await delay("00:00:05")
        assert mission.counter.get() == 678

    async def subtask(mission: TestMissionModel):
        assert mission.counter.get() == 123
        await delay("00:00:01")
        assert mission.counter.get() == 345
        mission.counter.set(678)

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", activity())),
                                       "24:00:00")
    assert spans == [Span("activity", Duration.ZERO, Duration.of(5, SECONDS)),]


def test_call():
    """
    Check that calling a child activity creates the correct spans, and that the parent resumes after the child finishes
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.set(123)
        await call(mission, other_activity(mission))
        assert mission.counter.get() == 345
        await delay("00:00:01")

    @TestMissionModel.ActivityType
    async def other_activity(mission: TestMissionModel):
        assert mission.counter.get() == 123
        await delay("00:00:01")
        assert mission.counter.get() == 123
        mission.counter.set(345)

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", activity())),
                                       "24:00:00")
    assert spans == [Span("activity", Duration.ZERO, Duration.of(2, SECONDS)),
                     Span("other_activity", Duration.ZERO, Duration.SECOND)]


def test_call_task():
    """
    Check that calling a child tas creates no new spans, and that the parent resumes after the child finishes
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.set(123)
        await call(mission, subtask(mission))
        assert mission.counter.get() == 345
        await delay("00:00:01")

    async def subtask(mission: TestMissionModel):
        assert mission.counter.get() == 123
        await delay("00:00:01")
        assert mission.counter.get() == 123
        mission.counter.set(345)

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", activity())),
                                       "24:00:00")
    assert spans == [Span("activity", Duration.ZERO, Duration.of(2, SECONDS)),]



def test_discrete_condition():
    """
    Check that a task is resumed correctly when a condition becomes true
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.set(123)
        await wait_until(lambda: mission.counter.get() == 345)
        assert mission.counter.get() == 345

    @TestMissionModel.ActivityType
    async def other_activity(mission: TestMissionModel):
        mission.counter.set(345)

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", activity()),
                                                                        ("00:00:15", other_activity())),
                                       "24:00:00")

    assert spans == [Span("activity", Duration.ZERO, Duration.of(15, SECONDS)),
                     Span("other_activity", Duration.of(15, SECONDS), Duration.ZERO)]


def test_concurrent_effects():
    """
    Make sure the counter gets incremented when expected by observing it from another activity
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.emit(lambda x: x + 1)
        assert mission.counter.get() == 1
        await delay("00:00:00")
        assert mission.counter.get() == 2

    simulate(TestMissionModel,
             Schedule.build(("00:00:00", activity()), ("00:00:00", activity())),
             "24:00:00")


def test_autonomous_condition():
    """
    Check that a task is resumed correctly when a condition becomes true
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        assert mission.linear.get()[0] == 0
        await delay("00:00:01")
        assert mission.linear.get()[0] == 1
        await delay("00:00:02")
        assert mission.linear.get()[0] == 3

    simulate(TestMissionModel, Schedule.build(("00:00:00", activity())), "24:00:00")


@pytest.mark.skip("Support for non-keyword args not yet implemented")
def test_activity_args():
    """
    Check that an activity receives args in the correct order
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel, number1, number2):
        assert number1 == 123
        assert number2 == 123

    simulate(TestMissionModel, Schedule.build(("00:00:00", activity(123, 345))), "24:00:00")

def test_activity_kwargs():
    """
    Check that an activity receives keyword args
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel, number1, number2):
        assert number1 == 123
        assert number2 == 345

    simulate(TestMissionModel, Schedule.build(("00:00:00", activity(number2=345, number1=123))), "24:00:00")


def test_validation():
    @TestMissionModel.ActivityType
    @Validation(lambda count: count > 0, "count must be positive")
    @Validation(lambda axis: axis in ["X", "Y", "Z"], "axis must be X, Y, or Z")
    @Validation(lambda count, axis: count > 10 if axis == "X" else True, "count must be at least 10 if axis is X")
    async def activity(mission: TestMissionModel, count, axis):
        pass

    assert activity(count=-1, axis="Z").validate() == [
        ValidationResult(False, "count must be positive"),
        ValidationResult(True, "axis must be X, Y, or Z"),
        ValidationResult(True, "count must be at least 10 if axis is X")
    ]

    assert activity(count=5, axis="X").validate() == [
        ValidationResult(True, "count must be positive"),
        ValidationResult(True, "axis must be X, Y, or Z"),
        ValidationResult(False, "count must be at least 10 if axis is X")
    ]

    assert activity(count=5, axis="Y").validate() == [
        ValidationResult(True, "count must be positive"),
        ValidationResult(True, "axis must be X, Y, or Z"),
        ValidationResult(True, "count must be at least 10 if axis is X")
    ]

    assert activity(count=11, axis="X").validate() == [
        ValidationResult(True, "count must be positive"),
        ValidationResult(True, "axis must be X, Y, or Z"),
        ValidationResult(True, "count must be at least 10 if axis is X")
    ]

    assert activity(count=5, axis=3.14).validate() == [
        ValidationResult(True, "count must be positive"),
        ValidationResult(False, "axis must be X, Y, or Z"),
        ValidationResult(True, "count must be at least 10 if axis is X")
    ]
