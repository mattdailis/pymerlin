from pymerlin._internal import _globals


# async def activity_wrapper(task, args, model, input_topic, output_topic):
#     if input_topic is not None:
#         _globals._current_context[0].emit(args, input_topic)
#     if task.execution_mode == TaskExecutionMode.ASYNC:
#         await task.__call__(model, **args)
#     else:
#         task.__call__(model, **args)
#     if output_topic is not None:
#         _globals._current_context[0].emit({}, output_topic)

def activity_wrapper(task, args, kwargs, input_topic, output_topic):
    from pymerlin._internal._decorators import TaskDefinition
    if type(task) is not TaskDefinition:
        raise ValueError("Hmm, why? " + repr(task))
    _globals._current_context[0].emit({}, input_topic)
    task.make_instance(*args, **kwargs).run()
    _globals._current_context[0].emit({}, output_topic)

def get_topics(func):
    from pymerlin._internal._decorators import TaskDefinition
    if type(func) is not TaskDefinition:
        raise Exception("Whoa there buddy")
    model_type = _globals._current_context[2]
    for activity_func, input_topic, output_topic in model_type.activity_types:
        if activity_func is func:
            return input_topic, output_topic
    return None, None
