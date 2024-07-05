class Duration:
    """
    A signed measure of the temporal distance between two instants.

    Durations are constructed by measuring a quantity of the provided units, such as {@link #SECOND} and {@link #HOUR}.
    This can be done in multiple ways:

    - Use the static factory method {@link Duration#of}, e.g. {@code Duration.of(5, SECONDS}
    - Use the static function {@link #duration}, e.g. {@code duration(5, SECONDS)}
    - Multiply an existing duration by a quantity, e.g. {@code SECOND.times(5)}

    Durations are internally represented as a fixed-point data type. The fixed-point representation preserves
    accuracy unlike floating-point arithmetic, which becomes less precise further from zero. Preserving accuracy is
    necessary in the domain of discrete event simulation. To ensure that causal/temporal orderings between timed
    elements in a simulation are preserved, it is necessary that operations on time quantities are exact. Arithmetic
    between fixed-point representations preserves such temporal orderings.

    The internal fixed-point representation of a Duration is a {@code long}. This representation is evident in
    the API where creating Durations and performing arithmetic operations often take a {@code long} as a parameter.
    As a result, any custom unit such as {@code DAY = duration(24, HOURS)} can be used directly with other
    Merlin-provided units like {@code SECONDS}.</p>

    A time value is represented as a {@code long} where an increment maps to number a specific time unit. Currently,
    the underlying time unit is microseconds, however, one should not rely on this always being the case. The maximum
    value of a fixed-point type is simply the largest value that can be represented by the underlying integer type.
    For a {@code long} this yields a range of (-2^63) to (2^63 - 1), or almost 600,000 years, at microsecond
    resolution.

    Note that derived units such as DAY, WEEK, MONTH, and YEAR are <em>not</em> included, because their values
    depend on properties of the particular calendrical system in use. For example:

    - The notion of "day" depends on the astronomical system against which time is measured.
    For example, the synodic (solar) day and the sidereal day are distinguished by which celestial body is held fixed
    in the sky by the passage of a day. (Synodic time fixes the body being orbited around; sidereal time
    fixes the far field of stars.)

    - The notion of "year" has precisely the same problem, with a similar synodic/sidereal distinction.

    -
    <p>
    The notion of "month" is worse, in that it depends on the presence of a *tertiary* body whose sygyzies with the
    other two bodies delimit integer quantities of the unit. (A syzygy is a collinear configuration of the bodies.)
    The lunar calendar (traditionally used in China) is based on a combination of lunar and solar
    synodic quantities. ("Month" derives from "moon".)
    </p>

    <p>
    The month of the Gregorian calendar is approximately a lunar synodic month, except that the definition was
    intentionally de-regularized (including intercalary days) in deference to the Earth's solar year.
    (Other calendars even invoke days *outside of any month*, which Wikipedia claims are called "epagomenal days".)
 *   In retrospect, it is unsurprising that ISO 8601 ordinal dates drop the month altogether,
 *   since "month" is a (complicated) derived notion in the Gregorian calendar.
 *   </p>
 *
 * <li>
 *   The notion of "week" seemingly has no basis in the symmetries of celestial bodies, and is instead a derived unit.
 *   Unfortunately, not only is it fundamentally based on the notion of "day", different calendars assign a different
 *   number of days to the span of a week.

 If you are working within the Gregorian calendar, the standard `java.time` package has you covered.

 If you are working with spacecraft, you may need to separate concepts such as "Earth day" and "Martian day", which
 are synodic periods measured against the Sun but from different bodies. Worse, you likely need to convert between
 such reference systems frequently, with a great deal of latitude in the choice of bodies being referenced.
 The gold standard is the well-known SPICE toolkit, coupled with a good set of ephemerides and clock kernels.

 If you're just looking for a rough estimate, you can define 24-hour days and 7-day weeks and 30-day months
 within your own domain in terms of the precise units we give here.
    """
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