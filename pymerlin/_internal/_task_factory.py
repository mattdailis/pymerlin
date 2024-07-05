class TaskFactory:
    def __init__(self, task_factory):
        self.task_factory = task_factory

    def create(self, executor):
        return self.task_factory.__call__()

    class Java:
        implements = ["gov.nasa.jpl.aerie.merlin.protocol.model.TaskFactory"]
