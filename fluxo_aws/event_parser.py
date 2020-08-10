import json
from functools import wraps


class ParsedEvent:
    def __init__(self, headers, query, body):
        self.headers = headers
        self.query = query
        self.body = body


def _load_resource(event, name):
    if name not in event.keys():
        resource = {}
    else:
        resource = event.get(name)
        if not resource:
            resource = {}
        elif type(resource) != dict:
            resource = json.loads(resource)
    return resource


def _parse_event(event):
    headers = _load_resource(event, "headers")
    query = _load_resource(event, "queryStringParameters")
    body = _load_resource(event, "body")
    return ParsedEvent(headers, query, body)


def event_parser(func):
    event_name = "event"

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = func.__code__.co_varnames
        if event_name in func_args:
            event = args[func_args.index(event_name)]
            list_args = list(args)
            list_args[func_args.index(event_name)] = _parse_event(event)
            args = tuple(list_args)
        elif event_name in kwargs.keys():
            event = kwargs[event_name]
            kwargs[event_name] = _parse_event(event)
        else:
            raise ValueError(f"{event_name} not in args or kwargs")
        return func(*args, **kwargs)

    return wrapper