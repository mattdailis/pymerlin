from pymerlin.framework import ModelType, simulate
from demo.model import Mission
from pymerlin.schedule import Schedule, Directive


def main():
    schedule = Schedule.build(
        ("00:00:01", Directive("activity1")),
        ("01:00:00", Directive("activity1")))
    duration = "01:00:00"
    profiles, spans, events = simulate(ModelType(Mission), schedule, duration)
    print(profiles)
    print(spans)
    print(events)


if __name__ == "__main__":
    main()
