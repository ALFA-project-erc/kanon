from functools import wraps


def list_to_tuple(func):

    def no_list(v):
        return tuple(v) if isinstance(v, list) else v

    @wraps(func)
    def wrapper(*args, **kwargs):
        args = (no_list(arg) for arg in args)
        kwargs = {k: no_list(v) for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapper
