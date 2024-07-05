from pymerlin import MissionModel
from pymerlin.model_actions import delay, wait_until, spawn


@MissionModel
class Mission:
    def __init__(self, registrar):
        self.cell1 = registrar.cell("init")

        registrar.resource("/cell1", self.cell1)
        registrar.topic("/cell1")

@Mission.ActivityType
async def activity1(mission):
    mission.cell1.emit("foo")
    result = mission.cell1.get()
    assert result == "foo", result
    await delay("00:00:12")
    mission.cell1.emit("bar")
    spawn(activity2(mission))

@Mission.ActivityType
async def activity2(mission):
    await wait_until(lambda: True)