from pymerlin._internal._globals import models_by_id
from pymerlin._internal._input_type import InputType
from pymerlin._internal._serialized_value import from_map_str_serialized_value
from pymerlin._internal._spawn_helpers import activity_wrapper
from pymerlin._internal._task import Task
from pymerlin._internal._task_factory import TaskFactory


class DirectiveType:
    def __init__(self, gateway, activity, input_topic, output_topic):
        self.gateway = gateway
        self.activity = activity
        self.input_topic = input_topic
        self.output_topic = output_topic

    def getInputType(self):
        return InputType()

    def getOutputType(self):
        return None

    def getTaskFactory(self, model_id, args):
        task_provider = lambda: activity_wrapper(self.activity, from_map_str_serialized_value(self.gateway, args), models_by_id[model_id][0], self.input_topic, self.output_topic)
        return TaskFactory(lambda: Task(self.gateway, models_by_id[model_id][1], task_provider))

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.DirectiveType"]
