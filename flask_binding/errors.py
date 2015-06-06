class BindingError(Exception):
    pass


class InvalidArgumentError(BindingError):
    def __init__(self, arg_name, *args, **kwargs):
        super().__init__(args, kwargs)
        self.arg_name = arg_name


class RequiredArgumentError(BindingError):
    def __init__(self, arg_name, *args, **kwargs):
        super().__init__(args, kwargs)
        self.arg_name = arg_name
