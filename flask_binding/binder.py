from .binders import PrimitiveBinder
from .errors import InvalidArgumentError
from .errors import RequiredArgumentError


class Binder(object):
    binders = {
        int: PrimitiveBinder(),
        str: PrimitiveBinder()
    }

    @staticmethod
    def bind(params):
        kwargs = {}

        for name, param in params.items():
            context = BindingContext()
            context.name = param.name or name
            context.type = param.type
            context.multiple = param.multiple
            context.values = param.get_values()

            binder = Binder.binders[param.type]

            try:
                value = binder.bind(context)
            except Exception as e:
                raise InvalidArgumentError(name, e)

            if value is None:
                if param.required:
                    raise RequiredArgumentError(name)
                value = param.default

            kwargs[name] = value

        return kwargs


class BindingContext(object):
    def __init__(self, type_=None, name=None, values=None, multiple=False):
        self.type = type_
        self.name = name
        self.values = values
        self.multiple = multiple
