from pymerlin import MissionModel, simulate, Schedule, Duration
from pymerlin._internal._decorators import Validation
from pymerlin._internal._registrar import CellRef
from pymerlin.model_actions import delay


@MissionModel
class Model:
    def __init__(self, registrar):
        self.counter: CellRef = registrar.cell(0)
        self.data_model = DataModel(registrar)
        registrar.resource("counter", self.counter.get)

@Model.ActivityType
async def increment_counter(model):
    counter = model.counter
    counter.set_value(counter.get() + 1)

class DataModel:
    def __init__(self, registrar):
        self.recording_rate = registrar.cell(0)
        registrar.resource("recording_rate", self.recording_rate.get)

@Model.ActivityType
@Validation(lambda rate: rate < 100.0, "Collection rate is beyond buffer limit of 100.0 Mbps")
async def create_data(model, rate=0.0, duration="01:00:00"):
    model.data_model.recording_rate += rate
    await delay(Duration.from_string(duration))
    model.data_model.recording_rate -= rate

from enum import Enum
class MagDataCollectionMode(Enum):
    OFF = 0.0  # kbps
    LOW_RATE = 500.0  # kbps
    HIGH_RATE = 5000.0  # kbps

def main():
    # print(simulate(
    #     Model,
    #     # Schedule.build(("00:00:01", Directive("create_data", {"rate": 20.0, "duration": "00:00:01"}))),
    #     Schedule.build(("00:00:01", create_data(rate=200.0, duration="00:00:01"))),
    #     "01:00:00"
    # ))
    print(MagDataCollectionMode.HIGH_RATE)

if __name__ == '__main__':
    main()
