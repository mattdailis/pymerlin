package gov.nasa.ammos.aerie.merlin.python;

import gov.nasa.jpl.aerie.merlin.driver.*;
import gov.nasa.jpl.aerie.merlin.protocol.model.ModelType;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import gov.nasa.jpl.aerie.merlin.protocol.types.Unit;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

public class Merlin {
    public Registrar registrar() {
        return new Registrar();
    }

    public <Config, Model> SimulationResults simulate(ModelType<Config, Model> modelType, Config config, Schedule schedule, Instant startTime, Duration duration) {
        final var builder = new MissionModelBuilder();
        final var builtModel = builder.build(modelType.instantiate(startTime, config, builder), DirectiveTypeRegistry.extract(modelType));
        return SimulationDriver.simulate(
                builtModel,
                adaptSchedule(schedule),
                startTime,
                duration,
                startTime,
                duration,
                () -> false
        );
    }

    private Map<ActivityDirectiveId, ActivityDirective> adaptSchedule(Schedule schedule) {
        final var res = new HashMap<ActivityDirectiveId, ActivityDirective>();
        for (var entry : schedule.entries()) {
            res.put(new ActivityDirectiveId(entry.id()),
                    new ActivityDirective(
                            entry.startOffset(),
                            entry.directive().type(),
                            entry.directive().arguments(),
                            null,
                            true));
        }
        return res;
    }

    public void simulate(ModelType<?, ?> modelType) {

        modelType.instantiate(Instant.EPOCH, null, null);
    }
}
