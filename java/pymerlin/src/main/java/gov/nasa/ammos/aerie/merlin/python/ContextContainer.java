package gov.nasa.ammos.aerie.merlin.python;

import gov.nasa.jpl.aerie.merlin.protocol.driver.CellId;
import gov.nasa.jpl.aerie.merlin.protocol.driver.Scheduler;

import java.util.Map;
import java.util.Objects;

public class ContextContainer {
    private static Context currentContext = null;

    public record Context(Map<SideBySideTest.Cell, CellId> cells, Scheduler scheduler) {}

    public static Context get() {
        return currentContext;
    }

    public static void set(Context context) {
        Objects.requireNonNull(context, "Use clear() instead");
        currentContext = context;
    }

    public static void clear() {
        currentContext = null;
    }
}
