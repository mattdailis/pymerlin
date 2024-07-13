from pymerlin._internal import _globals


async def activity_wrapper(task, args, model, input_topic, output_topic):
    if input_topic is not None:
        _globals._current_context[0].emit(args, input_topic)
    await task.__call__(model, **args)
    if output_topic is not None:
        _globals._current_context[0].emit({}, output_topic)

def get_topics(model_type, func):
    for activity_func, input_topic, output_topic in model_type.activity_types:
        if activity_func is func:
            return input_topic, output_topic
    return None, None
