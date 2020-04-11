from flask import request
from functools import wraps


def json_only(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        if not request.is_json:
            return {'ok': False, 'error': 'JSON Only!'}, 400
        return function(*args, **kwargs)
    return decorator


def required_args(*required):
    def inner(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            data = request.get_json()
            for arg in required:
                if data.get(arg) is None:
                    return {'ok': False, 'error': f'{arg} required!'}, 400
            return function(*args, **kwargs)
        return decorator
    return inner
