package gov.nasa.ammos.aerie.merlin.python;

import gov.nasa.jpl.aerie.merlin.protocol.driver.CellId;
import gov.nasa.jpl.aerie.merlin.protocol.driver.Initializer;
import gov.nasa.jpl.aerie.merlin.protocol.driver.Topic;
import gov.nasa.jpl.aerie.merlin.protocol.model.*;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import org.apache.commons.lang3.mutable.MutableObject;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;

public class SideBySideTest {
  private static final Instant START = Instant.EPOCH;
  private Registrar model;

  public record Cell<Event, Value>(
      Topic<Event> topic,
      Value initialValue,
      Function<List<Event>, Value> apply
  )
  {
    public static <Event, Value> Cell<Event, Value> of(
        Value initialValue,
        Function<List<Event>, Value> apply)
    {
      return new Cell<>(new Topic<>(), initialValue, apply);
    }

    public void emit(Event event) {
      ContextContainer.get().scheduler().emit(event, this.topic);
    }

    @SuppressWarnings("unchecked")
    public Value get() {
      final var context = ContextContainer.get();
      final var scheduler = context.scheduler();
      final var cellId = context.cells().get(this);
      return ((MutableObject<Value>) scheduler.get(Objects.requireNonNull(cellId))).getValue();
    }
  }

  private void delay(Duration duration) {
//    ContextContainer.get().threadedTask().thread().delay(duration);
  }

  private void waitUntil(Condition condition) {
//    ContextContainer.get().threadedTask().thread().waitUntil(condition);
  }

  private void call(TaskFactory<?> child) {
//    ContextContainer.get().threadedTask().thread().call(InSpan.Fresh, child);
  }


  public static <Event, Value> CellId<MutableObject<Value>> allocate(
      final Initializer builder,
      final Cell<Event, Value> cell)
  {
    return builder.allocate(
        new MutableObject<>(cell.initialValue()),
        new CellType<>() {
          @Override
          public EffectTrait<List<Event>> getEffectType() {
            return new EffectTrait<>() {
              @Override
              public List<Event> empty() {
                return List.of();
              }

              @Override
              public List<Event> sequentially(final List<Event> prefix, final List<Event> suffix) {
                final var res = new ArrayList<Event>(prefix);
                res.addAll(suffix);
                return res;
              }

              @Override
              public List<Event> concurrently(final List<Event> left, final List<Event> right) {
                if (left.isEmpty()) return right;
                if (right.isEmpty()) return left;
                throw new UnsupportedOperationException("Unsupported concurrent composition of non-empty lists");
              }
            };
          }

          @Override
          public MutableObject<Value> duplicate(final MutableObject<Value> mutableObject) {
            return new MutableObject<>(mutableObject.getValue());
          }

          @Override
          public void apply(final MutableObject<Value> mutableObject, final List<Event> o) {
            mutableObject.setValue(cell.apply().apply(o));
          }
        },
        List::of,
        cell.topic());
  }
}

