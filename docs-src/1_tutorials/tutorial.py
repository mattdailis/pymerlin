from pymerlin import MissionModel, simulate, Schedule, Directive
from pymerlin._internal._registrar import CellRef


@MissionModel
class FireSat:
    def __init__(self, registrar):
        self.counter: CellRef = registrar.cell(0)
        registrar.resource("counter", self.counter.get)

@FireSat.ActivityType
async def increment_counter(mission: FireSat):
    counter = mission.counter
    counter.set_value(counter.get() + 1)

def main():
    print(simulate(
        FireSat,
        Schedule.build(("00:00:01", Directive("increment_counter"))),
        "01:00:00"
    ))

if __name__ == '__main__':
    main()
