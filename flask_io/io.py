from flask import request
from functools import wraps
from .encoders import get_default_encoders
from .errors import ContentTypeNotSupported
from .errors import FlaskIOError
from .errors import InvalidArgumentError
from .errors import InvalidPayloadError
from .errors import RequiredArgumentError
from .errors import RequiredPayloadError
from .parsers import get_default_parsers


class FlaskIO(object):
    def __init__(self, app=None):
        self.__encoders = get_default_encoders()
        self.__parsers = get_default_parsers()

        if app:
            self.init_app(app)

    @property
    def encoders(self):
        return self.__encoders

    @property
    def parsers(self):
        return self.__parsers

    def init_app(self, app):
        pass

    def from_body(self, param_name, param_type, required=False, validate=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__decode_body_into_param(kwargs, param_name, param_type, required, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_cookie(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__parse_arg_into_param(kwargs, param_name, param_type, request.cookies, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_form(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__parse_arg_into_param(kwargs, param_name, param_type, request.form, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_header(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__parse_arg_into_param(kwargs, param_name, param_type, request.headers, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_query(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__parse_arg_into_param(kwargs, param_name, param_type, request.args, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def __decode_body_into_param(self, params, param_name, param_type, required, validate):
        content_type = request.headers['content-type']
        data = request.get_data()

        if not data and required:
            raise RequiredPayloadError()

        encoder = self.__encoders.get(content_type)

        if not encoder:
            raise ContentTypeNotSupported(content_type)

        param_value = encoder.decode(data)

        if type(param_value) != param_type:
            raise InvalidPayloadError()

        if validate:
            try:
                success = validate(param_value)
            except Exception as e:
                raise InvalidPayloadError(e)

            if not success:
                raise InvalidPayloadError()

        params[param_name] = param_value

    def __parse_arg_into_param(self, params, param_name, param_type, args, arg_name, default, required, multiple, validate):
        if not arg_name:
            arg_name = param_name

        parser = self.__parsers.get(param_type)

        if not parser:
            raise FlaskIOError('Parameter type \'%s\'does not have a parser.' % str(param_type))

        try:
            if multiple:
                arg_values = args.getlist(arg_name) or [None]
                param_values = []
                for arg_value in arg_values:
                    param_values.append(self.__parse_arg(parser, arg_name, arg_value, default, required, validate))
                params[param_name] = param_values
            else:
                arg_value = args.get(arg_name)
                params[param_name] = self.__parse_arg(parser, arg_name, arg_value, default, required, validate)
        except Exception as e:
            if isinstance(e, (InvalidArgumentError, RequiredArgumentError)):
                raise
            raise InvalidArgumentError(arg_name, e)

    @staticmethod
    def __parse_arg(parser, arg_name, arg_value, default, required, validate):
        if arg_value:
            arg_value = parser.parse(arg_value)

        if not arg_value:
            if required:
                raise RequiredArgumentError(arg_name)

            if default:
                if callable(default):
                    arg_value = default()
                else:
                    arg_value = default

        if validate:
            try:
                success = validate(arg_name, arg_value)
            except Exception as e:
                raise InvalidArgumentError(arg_name, e)

            if not success:
                raise InvalidArgumentError(arg_name)

        return arg_value
