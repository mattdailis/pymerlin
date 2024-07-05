import pytest

from pymerlin import MissionModel
from pymerlin.duration import Duration, SECONDS
from pymerlin import simulate, Span
from pymerlin.model_actions import delay, spawn, call, wait_until
from pymerlin import Schedule, Directive

from py4j.java_gateway import Py4JJavaError


@MissionModel
class TestMissionModel:
    def __init__(self, registrar):
        self.list = registrar.cell([])
        self.counter = registrar.cell(0)
        # self.linear = registrar.cell(line(0, 1))


class LinearCell:
    def __init__(self, initial, rate_per_second):
        self.initial = initial
        self.rate_per_second = rate_per_second

    def step(self, duration):
        self.initial += duration.times(self.rate_per_second * 1_000_000)

    def duplicate(self):
        return LinearCell(self.initial, self.rate_per_second)



def line(initial, rate_per_second):
    return LinearCell(initial, rate_per_second)



@TestMissionModel.ActivityType
async def noop(mission):
    pass


@TestMissionModel.ActivityType
async def add_to_list(mission, item):
    mission.counter.emit(mission.counter.get() + 1)
    mission.list.emit(mission.list.get() + [item])


@TestMissionModel.ActivityType
async def delay_one_hour(mission):
    mission.counter.emit(mission.counter.get() + 1)
    await delay("01:00:00")


@TestMissionModel.ActivityType
async def clear_list(mission, item):
    mission.counter.emit(mission.counter.get() + 1)
    mission.list.emit([])


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
    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:01", Directive("noop"))), "24:00:00")
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
             Schedule.build(("00:00:00", Directive("activity")), ("00:00:01", Directive("delay_one_hour"))), "24:00:00")


def test_exception():
    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        await delay("00:00:00")
        raise Exception("Exception in task!")

    with pytest.raises(Py4JJavaError) as e:
        simulate(TestMissionModel, Schedule.build(("00:00:00", Directive("activity"))), "24:00:00")
        # TODO make sure ample information is extracted from the java exception


@pytest.mark.skip("This test hangs, but it would be nice if it raised an exception instead")
def test_forgot_to_await():
    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        delay("00:00:01")
        delay("00:00:01")

    with pytest.raises(Py4JJavaError) as e:
        simulate(TestMissionModel, Schedule.build(("00:00:00", Directive("activity"))), "24:00:00")
        # TODO make sure ample information is extracted from the java exception

    print()


def test_spawn():
    """
    Check that spawning a child activity creates the correct spans, and that concurrent events become visible after yield
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.emit(123)
        spawn(other_activity(mission))
        mission.counter.emit(345)
        assert mission.counter.get() == 345

    @TestMissionModel.ActivityType
    async def other_activity(mission: TestMissionModel):
        assert mission.counter.get() == 123
        await delay("00:00:01")
        assert mission.counter.get() == 345

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", Directive("activity"))),
                                       "24:00:00")
    assert spans == [Span("activity", Duration.ZERO, Duration.SECOND),
                     Span("other_activity", Duration.ZERO, Duration.SECOND)]


def test_call():
    """
    Check that calling a child activity creates the correct spans, and that the parent resumes after the child finishes
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.emit(123)
        await call(other_activity(mission))
        assert mission.counter.get() == 345
        await delay("00:00:01")

    @TestMissionModel.ActivityType
    async def other_activity(mission: TestMissionModel):
        assert mission.counter.get() == 123
        await delay("00:00:01")
        assert mission.counter.get() == 123
        mission.counter.emit(345)

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", Directive("activity"))),
                                       "24:00:00")
    assert spans == [Span("activity", Duration.ZERO, Duration.of(2, SECONDS)),
                     Span("other_activity", Duration.ZERO, Duration.SECOND)]


def test_discrete_condition():
    """
    Check that a task is resumed correctly when a condition becomes true
    """

    @TestMissionModel.ActivityType
    async def activity(mission: TestMissionModel):
        mission.counter.emit(123)
        await wait_until(lambda: mission.counter.get() == 345)
        assert mission.counter.get() == 345

    @TestMissionModel.ActivityType
    async def other_activity(mission: TestMissionModel):
        mission.counter.emit(345)

    profiles, spans, events = simulate(TestMissionModel, Schedule.build(("00:00:00", Directive("activity")),
                                                                        ("00:00:15", Directive("other_activity"))),
                                       "24:00:00")

    assert spans == [Span("activity", Duration.ZERO, Duration.of(15, SECONDS)),
                     Span("other_activity", Duration.of(15, SECONDS), Duration.ZERO)]


def test_continuous_condition():
    pass
