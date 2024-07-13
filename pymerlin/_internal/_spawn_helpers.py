from pymerlin._internal import _globals
from pymerlin._internal._decorators import ActivityDefinition
from pymerlin._internal._execution_mode import TaskExecutionMode


# async def activity_wrapper(task, args, model, input_topic, output_topic):
#     if input_topic is not None:
#         _globals._current_context[0].emit(args, input_topic)
#     if task.execution_mode == TaskExecutionMode.ASYNC:
#         await task.__call__(model, **args)
#     else:
#         task.__call__(model, **args)
#     if output_topic is not None:
#         _globals._current_context[0].emit({}, output_topic)

def activity_wrapper(task, args, model, input_topic, output_topic):
    if input_topic is not None:
        _globals._current_context[0].emit(args, input_topic)
    task.__call__(model, **args)
    if output_topic is not None:
        _globals._current_context[0].emit({}, output_topic)

def get_topics(model_type, func):
    if type(func) is not ActivityDefinition:
        raise Exception("Whoa there buddy")
    for activity_func, input_topic, output_topic in model_type.activity_types:
        if activity_func is func:
            return input_topic, output_topic
    return None, None
