from datetime import datetime
from flask import request
from functools import wraps
from inspect import isfunction
from .parsers import BooleanParser
from .parsers import DateTimeParser
from .parsers import PrimitiveParser
from .errors import InvalidArgumentError
from .errors import RequiredArgumentError


class FlaskIO(object):
    def __init__(self, app=None):
        self.__parsers = {
            bool: BooleanParser(),
            int: PrimitiveParser(int),
            float: PrimitiveParser(float),
            str: PrimitiveParser(str),
            datetime: DateTimeParser()
        }

        if app:
            self.init_app(app)

    @property
    def parsers(self):
        return self.__parsers

    def init_app(self, app):
        pass

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

    def __parse_arg_into_param(self, params, param_name, param_type, args, arg_name, default, required, multiple, validate):
        if not arg_name:
            arg_name = param_name

        parser = self.__parsers.get(param_type)

        if not parser:
            raise Exception('Parameter type \'%s\'does not have a parser.' % str(param_type))

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
                if isfunction(default):
                    arg_value = default()
                else:
                    arg_value = default

        if validate:
            try:
                success = validate(arg_value)
            except Exception as e:
                raise InvalidArgumentError(arg_name, e)

            if not success:
                raise InvalidArgumentError(arg_name)

        return arg_value
