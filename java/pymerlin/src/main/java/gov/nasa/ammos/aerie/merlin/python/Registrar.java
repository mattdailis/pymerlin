package gov.nasa.ammos.aerie.merlin.python;

import gov.nasa.jpl.aerie.merlin.protocol.driver.*;
import gov.nasa.jpl.aerie.merlin.protocol.model.*;
import gov.nasa.jpl.aerie.merlin.protocol.types.InSpan;
import gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue;
import gov.nasa.jpl.aerie.merlin.protocol.types.Unit;
import gov.nasa.jpl.aerie.merlin.protocol.types.ValueSchema;
import org.apache.commons.lang3.tuple.Pair;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

public final class Registrar {
  List<Pair<String, Consumer<Object>>> activities = new ArrayList<>();
  List<SideBySideTest.Cell<?, ?>> cells = new ArrayList<>();
  List<Runnable> daemons = new ArrayList<>();
  List<Pair<String, Supplier<?>>> resources = new ArrayList<>();

  public <T> SideBySideTest.Cell<T, T> cell(T initialValue) {
    return this.cell(initialValue, List::getLast);
  }

  public <T> SideBySideTest.Cell<T, T> cell(T initialValue, Function<List<T>, T> apply) {
    final var cell = SideBySideTest.Cell.of(initialValue, apply);
    cells.add(cell);
    return cell;
  }

  public void activity(String name, Consumer<Object> effectModel) {
    this.activities.add(Pair.of(name, effectModel));
  }

  public void daemon(Runnable runnable) {
    this.daemons.add(runnable);
  }

  public <T> void resource(String name, Supplier<T> supplier) {
    this.resources.add(Pair.of(name, supplier));
  }

  public ModelType<Unit, Map<SideBySideTest.Cell, CellId>> asModelType() {
    final var directives = new HashMap<String, DirectiveType<Map<SideBySideTest.Cell, CellId>, Map<String, SerializedValue>, Unit>>();
    final var inputTopics = new HashMap<String, Topic<Unit>>();
    final var outputTopics = new HashMap<String, Topic<Unit>>();

    for (final var activity : activities) {
      final Topic<Unit> inputTopic = new Topic<>();
      final Topic<Unit> outputTopic = new Topic<>();
      inputTopics.put(activity.getLeft(), inputTopic);
      outputTopics.put(activity.getLeft(), outputTopic);
      directives.put(activity.getKey(), new DirectiveType<>() {

        @Override
        public InputType<Map<String, SerializedValue>> getInputType() {
          return Stubs.PASS_THROUGH_INPUT_TYPE;
        }

        @Override
        public OutputType<Unit> getOutputType() {
          return Stubs.UNIT_OUTPUT_TYPE;
        }

        @Override
        public TaskFactory<Unit> getTaskFactory(final Map<SideBySideTest.Cell, CellId> cellMap, final Map<String, SerializedValue> args) {
//          return executor -> PythonTaskHandle.of(executor, cellMap, () -> {
////            ContextContainer.get().scheduler().startActivity(Unit.UNIT, inputTopic);
//            activity.getValue().accept(Unit.UNIT);
////            ContextContainer.get().scheduler().endActivity(Unit.UNIT, outputTopic);
//            return Unit.UNIT;
//          });
          return null;
        }
      });
    }


    return new ModelType<>() {
      @Override
      public Map<String, ? extends DirectiveType<Map<SideBySideTest.Cell, CellId>, ?, ?>> getDirectiveTypes() {
        return directives;
      }

      @Override
      public InputType<Unit> getConfigurationType() {
        return Stubs.UNIT_INPUT_TYPE;
      }

      @Override
      public Map<SideBySideTest.Cell, CellId> instantiate(
          final Instant planStart,
          final Unit configuration,
          final Initializer builder)
      {
        final var cellMap = new HashMap<SideBySideTest.Cell, CellId>();
        for (final var directive : directives.entrySet()) {
          builder.topic(
              "ActivityType.Input." + directive.getKey(),
              inputTopics.get(directive.getKey()),
              Stubs.UNIT_OUTPUT_TYPE);
          builder.topic(
              "ActivityType.Output." + directive.getKey(),
              outputTopics.get(directive.getKey()),
              Stubs.UNIT_OUTPUT_TYPE);
        }
        for (final var cell : cells) {
          cellMap.put(cell, SideBySideTest.allocate(builder, cell));
        }
        for (final var daemon : daemons) {
//          builder.daemon(executor -> PythonTaskHandle.of(executor, cellMap, () -> {daemon.run(); return Unit.UNIT;}));
        }
        for (final var resource : resources) {
          builder.resource(resource.getLeft(), new Resource<Object>() {
            @Override
            public String getType() {
              return "discrete";
            }

            @Override
            public OutputType<Object> getOutputType() {
              return new OutputType<>() {
                @Override
                public ValueSchema getSchema() {
                  return ValueSchema.ofStruct(Map.of());
                }

                @Override
                public SerializedValue serialize(final Object value) {
                  return SerializedValue.of(value.toString());
                }
              };
            }

            @Override
            public Object getDynamics(final Querier querier) {
              ContextContainer.set(new ContextContainer.Context(cellMap, schedulerOfQuerier(querier)));
              try {
                  return resource.getRight().get();
              } finally {
                ContextContainer.clear();
              }
            }
          });
        }
        return cellMap;
      }
    };
  }

  private Scheduler schedulerOfQuerier(Querier querier) {
    return new Scheduler() {
      @Override
      public <State> State get(final CellId<State> cellId) {
        return querier.getState(cellId);
      }

      @Override
      public <Event> void emit(final Event event, final Topic<Event> topic) {
        throw new UnsupportedOperationException();
      }

      @Override
      public void spawn(final InSpan taskSpan, final TaskFactory<?> task) {
        throw new UnsupportedOperationException();
      }
    };
  }
}
