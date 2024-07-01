package gov.nasa.ammos.aerie.merlin.python;

import gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue;

import java.util.Map;

public record Directive(String type, Map<String, SerializedValue> arguments) {
}
