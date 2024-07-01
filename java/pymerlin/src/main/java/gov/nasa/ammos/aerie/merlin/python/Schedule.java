package gov.nasa.ammos.aerie.merlin.python;

import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import org.apache.commons.lang3.tuple.Pair;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.concurrent.atomic.AtomicLong;

public record Schedule(List<ScheduleEntry> entries) {
    public record ScheduleEntry(long id, Duration startTime, Directive directive) {
        public Duration startOffset() {
            return startTime;
        }
    }

    @SafeVarargs
    public static Schedule build(Pair<Duration, Directive>... entries) {
        var id = new AtomicLong(0L);
        return new Schedule(Arrays.stream(entries).map($ -> new ScheduleEntry(id.getAndIncrement(), $.getLeft(), $.getRight())).toList());
    }

    public static Schedule empty() {
        return Schedule.build();
    }

    public Schedule put(long id, Duration startTime, Directive directive) {
      final var newEntries = new ArrayList<ScheduleEntry>();
      for (final var entry : this.entries) {
        if (entry.id != id) {
          newEntries.add(entry);
        }
      }
      newEntries.add(new ScheduleEntry(id, startTime, directive));
      return new Schedule(newEntries);
    }

  public Schedule putAll(Schedule other) {
    final var newEntries = new ArrayList<ScheduleEntry>();
    final var reservedIds = new HashSet<Long>();
    for (final var entry : other.entries) {
      reservedIds.add(entry.id);
    }
    for (final var entry : this.entries) {
      if (!reservedIds.contains(entry.id)) {
        newEntries.add(entry);
      }
    }
    newEntries.addAll(other.entries);
    return new Schedule(newEntries);
  }

    public ScheduleEntry get(long id) {
        for (ScheduleEntry entry : entries) {
            if (entry.id() == id) {
                return entry;
            }
        }
        throw new NoSuchElementException();
    }

    public Schedule plus(Schedule other) {
      var newEntries = new ArrayList<>(this.entries);
      var id = 0L;
      for (final var entry : this.entries) {
        newEntries.add(new ScheduleEntry(id++, entry.startTime, entry.directive));
      }
      for (final var entry : other.entries) {
        newEntries.add(new ScheduleEntry(id++, entry.startTime, entry.directive));
      }
      return new Schedule(newEntries);
    }

    public int size() {
        return entries.size();
    }
}
