from inspect import isclass


def new_if_isclass(value):
    if isclass(value):
        return value()
    return value


def unpack(value):
    data, status, headers = value + (None,) * (3 - len(value))
    return data, status, headers
