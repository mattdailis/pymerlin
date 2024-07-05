from py4j.java_collections import MapConverter

from pymerlin._internal._cell_type import CellType
from pymerlin._internal._directive_type import DirectiveType
from pymerlin._internal._globals import models_by_id
from pymerlin._internal._output_type import OutputType
from pymerlin._internal._registrar import Registrar
from pymerlin._internal._resource import Resource


class ModelType:
    def __init__(self, model_class):
        self.gateway = None
        self.model_class = model_class
        self.raw_activity_types = model_class.activity_types
        self.activity_types = []

    def set_gateway(self, gateway):
        self.gateway = gateway
        self.activity_types = []
        for activity in self.raw_activity_types.values():
            self.activity_types.append((activity, gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.driver.Topic(),
                                        gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.driver.Topic()))

    def instantiate(self, start_time, config, builder):
        registrar = Registrar()
        model = self.model_class(registrar)

        default_cell_type = CellType(self.gateway)
        for cell_ref, initial_value, evolution in registrar.cells:
            cell_type = default_cell_type if evolution is None else CellType(self.gateway, evolution=evolution)
            topic = self.gateway.jvm.gov.nasa.jpl.aerie.merlin.protocol.driver.Topic()
            cell_id = builder.allocate(self.gateway.jvm.org.apache.commons.lang3.mutable.MutableObject(initial_value),
                                       cell_type, self.gateway.jvm.java.util.function.Function.identity(), topic)
            cell_ref.id = cell_id
            cell_ref.topic = topic

        for activity, input_topic, output_topic in self.activity_types:
            activity_type_name = activity.__name__
            builder.topic(f"ActivityType.Input.{activity_type_name}", input_topic, OutputType(self.gateway))
            builder.topic(f"ActivityType.Output.{activity_type_name}", output_topic, OutputType(self.gateway))

        for resource_name, resource_func in registrar.resources:
            builder.resource(resource_name, Resource(self.gateway, resource_func))

        models_by_id[id(model)] = model, self
        return id(model)

    def getDirectiveTypes(self):
        return MapConverter().convert(
            {
                activity_type[0].__name__: DirectiveType(
                    self.gateway,
                    activity_type[0],  # function
                    activity_type[1],  # input_topic
                    activity_type[2])  # output_topic
                for activity_type in self.activity_types
            },
            self.gateway._gateway_client)

    def getConfigurationType(self):
        pass

    def toString(self):
        return str(self)

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.ModelType"]