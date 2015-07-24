def unpack(value):
    if not isinstance(value, tuple):
        return value, 200, {}

    data, status, headers = value + (None,) * (3 - len(value))
    return data, status, headers
