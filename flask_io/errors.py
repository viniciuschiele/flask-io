class Error(object):
    def __init__(self, message, code=None, location=None, field=None, **kwargs):
        self.message = message
        self.code = code
        self.location = location
        self.field = field
        self.__dict__.update(kwargs)

    def as_dict(self):
        data = self.__dict__.copy()

        for key in set(data.keys()):
            if data[key] is None:
                data.pop(key)

        return data
