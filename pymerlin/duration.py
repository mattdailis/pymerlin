class Duration:
    def __init__(self, micros):
        self.micros = micros

    def times(self, scalar):
        return Duration(self.micros * scalar)

    def plus(self, other):
        return Duration(self.micros + other.micros)

    def negate(self):
        return Duration(-self.micros)

    @staticmethod
    def of(scalar, unit):
        return unit.times(scalar)

    @staticmethod
    def from_string(duration_string):
        """
        Examples:
        00:00:00.000000
        00:00:00.0
        00:00:00

        :param duration_string:
        :return:
        """
        is_negative = False
        hours, minutes, seconds_string = duration_string.split(":")
        assert len(minutes) == 2
        if hours.startswith("-"):
            is_negative = True
            hours = hours[1:]
        elif hours.startswith("+"):
            is_negative = False
            hours = hours[1:]
        hours = int(hours)
        minutes = int(minutes)
        if "." in seconds_string:
            seconds, subseconds = seconds_string.split(".")
        else:
            seconds = seconds_string
            subseconds = "000000"
        assert len(seconds) == 2
        seconds = int(seconds)
        if len(subseconds) > 6:
            subseconds = subseconds[:6]
        while len(subseconds) < 6:
            subseconds += "0"
        subseconds = int(subseconds)

        result = Duration.of(hours, HOURS).plus(Duration.of(minutes, MINUTES)).plus(Duration.of(seconds, SECONDS)).plus(Duration.of(subseconds, MICROSECONDS))
        if is_negative:
            return result.negate()
        else:
            return result

    def __repr__(self):
        if self.micros < 0:
            is_negative = True
            micros = -self.micros
        else:
            is_negative = False
            micros = self.micros
        hours = int(micros / HOURS.micros)
        micros -= hours * HOURS.micros
        minutes = int(micros / MINUTES.micros)
        assert minutes < 60
        micros -= minutes * MINUTES.micros
        seconds = int(micros / SECONDS.micros)
        assert seconds < 60
        micros -= seconds * SECONDS.micros
        microseconds = micros
        assert microseconds < 1_000_000, microseconds
        sign = "-" if is_negative else "+"
        return sign + str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2) + "." + str(microseconds).zfill(6)

    def __eq__(self, other):
        return type(other) == type(self) and self.micros == other.micros

    def __gt__(self, other):
        return self.micros.__gt__(other)

    def __ge__(self, other):
        return self.micros.__ge__(other)

    def __lt__(self, other):
        return self.micros.__lt__(other)

    def __le__(self, other):
        return self.micros.__le__(other)

Duration.ZERO = Duration(0)
Duration.MICROSECOND = Duration(1)
Duration.MICROSECONDS = Duration.MICROSECOND
Duration.MILLISECOND = Duration.MICROSECONDS.times(1000)
Duration.MILLISECONDS = Duration.MILLISECOND
Duration.SECOND = Duration.MILLISECONDS.times(1000)
Duration.SECONDS = Duration.SECOND
Duration.MINUTE = Duration.SECOND.times(60)
Duration.MINUTES = Duration.MINUTE
Duration.HOUR = Duration.MINUTE.times(60)
Duration.HOURS = Duration.HOUR

ZERO = Duration.ZERO
MICROSECOND = Duration.MICROSECOND
MICROSECONDS = Duration.MICROSECONDS
MILLISECOND = Duration.MILLISECOND
MILLISECONDS = Duration.MILLISECONDS
SECOND = Duration.SECOND
SECONDS = Duration.SECONDS
MINUTE = Duration.MINUTE
MINUTES = Duration.MINUTES
HOUR = Duration.HOUR
HOURS = Duration.HOURS


if __name__ == "__main__":
    print(Duration.from_string("00:00:00.000"))
    print(Duration.from_string("+00:00:00.000"))
    print(Duration.from_string("-00:00:00.000"))
    print(Duration.from_string("-01:00:00.000"))