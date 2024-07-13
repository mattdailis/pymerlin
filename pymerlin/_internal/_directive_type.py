from pymerlin._internal._decorators import TaskDefinition
from pymerlin._internal._globals import models_by_id
from pymerlin._internal._input_type import InputType

class DirectiveType:
    def __init__(self, gateway, activity, input_topic, output_topic, model_type):
        if type(activity) is not TaskDefinition:
            raise ValueError("Activity must be of type TaskDefinition, but was: " + repr(activity))
        self.gateway = gateway
        self.activity = activity
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.model_type = model_type

    def getInputType(self):
        return InputType()

    def getOutputType(self):
        return None

    def getTaskFactory(self, model_id, args):
        return self.activity.get_task_factory(models_by_id[model_id][0], args, self.gateway, self.model_type)

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.DirectiveType"]
