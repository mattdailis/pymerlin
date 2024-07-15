# from pymerlin import MissionModel, simulate, Schedule, Duration
# from pymerlin._internal._decorators import Validation, Task
# from pymerlin._internal._registrar import CellRef
# from pymerlin._internal._schedule import Directive
# from pymerlin.model_actions import delay, spawn_task
#
#
# @MissionModel
# class Model:
#     def __init__(self, registrar):
#         self.counter: CellRef = registrar.cell(0)
#         self.data_model = DataModel(registrar)
#         registrar.resource("counter", self.counter.get)
#
# @Model.ActivityType
# def increment_counter(model):
#     counter = model.counter
#     counter.set_value(counter.get() + 1)
#
# class DataModel:
#     def __init__(self, registrar):
#         self.recording_rate = registrar.cell(0)
#         registrar.resource("recording_rate", self.recording_rate.get)
#
#         self.ssr_volume_simple = registrar.cell(0.0)
#         registrar.resource("ssr_volume_simple", self.ssr_volume_simple.get)
#
#         self.ssr_volume_sampled = registrar.cell(0.0)
#         registrar.resource("ssr_volume_sampled", self.ssr_volume_sampled.get)
#
#         spawn_task(integrate_sampled_ssr, dict(data_model=self))
#
# INTEGRATION_SAMPLE_INTERVAL = Duration.of(60, Duration.SECONDS)
#
# @Task
# def integrate_sampled_ssr(data_model: DataModel):
#     while (True):
#         delay(INTEGRATION_SAMPLE_INTERVAL)
#         current_recording_rate = data_model.recording_rate.get()
#         data_model.ssr_volume_sampled += (
#                 current_recording_rate
#                 * INTEGRATION_SAMPLE_INTERVAL.to_number_in(Duration.SECONDS)
#                 / 1000.0)  # Mbit -> Gbit
#
# @Model.ActivityType
# @Validation(lambda rate: rate < 100.0, "Collection rate is beyond buffer limit of 100.0 Mbps")
# def collect_data(model, rate=0.0, duration="01:00:00"):
#     duration = Duration.from_string(duration)
#     model.data_model.recording_rate += rate
#     delay(duration)
#     model.data_model.ssr_volume_simple += rate * duration.to_number_in(Duration.SECONDS) / 1000.0
#     model.data_model.recording_rate -= rate
#
# from enum import Enum
# class MagDataCollectionMode(Enum):
#     OFF = 0.0  # kbps
#     LOW_RATE = 500.0  # kbps
#     HIGH_RATE = 5000.0  # kbps
#
# def main():
#     print(simulate(
#         Model,
#         Schedule.build(("00:00:01", Directive("collect_data", {"rate": 20.0, "duration": "00:00:01"}))),
#         # Schedule.build(("00:00:01", collect_data(rate=200.0, duration="00:00:01"))),
#         "01:00:00"
#     ))
#
# if __name__ == '__main__':
#     main()


from pymerlin import MissionModel, Duration
from pymerlin._internal._decorators import Validation
from pymerlin.model_actions import delay

@MissionModel
class Model:
    def __init__(self, registrar):
        self.data_model = DataModel(registrar)

class DataModel:
    def __init__(self, registrar):
        self.recording_rate = registrar.cell(0)
        registrar.resource("recording_rate", self.recording_rate.get)

@Model.ActivityType
@Validation(lambda rate: rate < 100.0, "Collection rate is beyond buffer limit of 100.0 Mbps")
def collect_data(model, rate=0.0, duration="01:00:00"):
    model.data_model.recording_rate += rate
    delay(Duration.from_string(duration))
    model.data_model.recording_rate -= rate

if __name__ == "__main__":
    from pymerlin import simulate, Schedule, Directive
    print(simulate(
        Model,
        Schedule.build(("00:00:01", Directive("collect_data", {"rate": 20.0, "duration": "00:00:01"}))),
        "01:00:00"
    ))