from datetime import datetime
from functools import wraps
from inspect import isfunction
from .parsers import BooleanParser
from .parsers import DateTimeParser
from .parsers import PrimitiveParser
from .errors import InvalidArgumentError
from .errors import RequiredArgumentError
from .sources import BodySource
from .sources import CookieSource
from .sources import FormSource
from .sources import HeaderSource
from .sources import QuerySource


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

    def from_body(self, param_name, type_, default=None, required=False, validate=None):
        return self.__from_source(BodySource, param_name, type_, default, required, False, validate, param_name)

    def from_cookie(self, param_name, type_, default=None, required=False, multiple=False, validate=None, arg_name=None):
        return self.__from_source(CookieSource, param_name, type_, default, required, multiple, validate, arg_name)

    def from_form(self, param_name, type_, default=None, required=False, multiple=False, validate=None, arg_name=None):
        return self.__from_source(FormSource, param_name, type_, default, required, multiple, validate, arg_name)

    def from_header(self, param_name, type_, default=None, required=False, multiple=False, validate=None, arg_name=None):
        return self.__from_source(HeaderSource, param_name, type_, default, required, multiple, validate, arg_name)

    def from_query(self, param_name, type_, default=None, required=False, multiple=False, validate=None, arg_name=None):
        return self.__from_source(QuerySource, param_name, type_, default, required, multiple, validate, arg_name)

    def __parse(self, source, name, type_, default, required, multiple, validate):
        try:
            values = source.get_value(name, multiple)

            parser = self.__parsers.get(type_)

            if isinstance(values, list):
                if len(values) == 0:
                    values.append(None)
            else:
                values = [values]

            for i in range(len(values)):
                value = values[i]
                value = None if value is None else parser.parse(value)

                if value is None:
                    if required:
                        raise RequiredArgumentError(name)

                    if default:
                        if isfunction(default):
                            value = default()
                        else:
                            value = default

                if validate:
                    try:
                        success = validate(value)
                    except Exception as e:
                        raise InvalidArgumentError(name, e)

                    if not success:
                        raise InvalidArgumentError(name)

                values[i] = value

            if multiple:
                return values

            return values[0]
        except Exception as e:
            if isinstance(e, (InvalidArgumentError, RequiredArgumentError)):
                raise
            raise InvalidArgumentError(name, e)

    def __from_source(self, source_cls, param_name, type_, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                source = source_cls()
                kwargs[param_name] = self.__parse(source, arg_name or param_name, type_, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator
