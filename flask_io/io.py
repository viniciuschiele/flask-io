# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import request
from functools import wraps
from werkzeug.exceptions import InternalServerError, NotAcceptable
from .encoders import register_default_decoders
from .encoders import register_default_encoders
from .errors import ErrorReason
from .errors import FlaskIOError
from .errors import ValidationError
from .parsers import register_default_parsers
from .utils import get_best_match_for_content_type, new_if_isclass, unpack


class FlaskIO(object):
    default_encoder = None

    def __init__(self, app=None):
        self.__app = None
        self.__decoders = {}
        self.__encoders = {}
        self.__parsers = {}

        register_default_decoders(self)
        register_default_encoders(self)
        register_default_parsers(self)

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.__app = app
        self.__app.before_first_request(self.__register_views)

    def register_decoder(self, media_type, func):
        self.__decoders[media_type] = func

    def register_encoder(self, media_type, func):
        if not self.default_encoder:
            self.default_encoder = media_type
        self.__encoders[media_type] = func

    def register_parser(self, type_, func):
        self.__parsers[type_] = func

    def from_body(self, param_name, param_type, schema=None, required=False, validate=None):
        schema = new_if_isclass(schema)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__fill_param_from_body(kwargs, param_name, param_type, schema, required, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_cookie(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__fill_param_from_args(kwargs, param_name, param_type, request.cookies, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_form(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__fill_param_from_args(kwargs, param_name, param_type, request.form, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_header(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__fill_param_from_args(kwargs, param_name, param_type, request.headers, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_query(self, param_name, param_type, default=None, required=False, multiple=False, validate=None, arg_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.__fill_param_from_args(kwargs, param_name, param_type, request.args, arg_name, default, required, multiple, validate)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def marshal_with(self, schema, model=None):
        schema = new_if_isclass(schema)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                data = func(*args, **kwargs)
                if isinstance(data, tuple):
                    data, status, headers = unpack(data)
                    return self.__marshal(data, schema, model), status, headers
                else:
                    return self.__marshal(data, schema, model)
            return wrapper
        return decorator

    def make_response(self, data):
        status = headers = None
        if isinstance(data, tuple):
            data, status, headers = unpack(data)

        if not isinstance(data, self.__app.response_class):
            media_type = request.accept_mimetypes.best_match(self.__encoders, default=self.default_encoder)
            encoder = self.__encoders.get(media_type)

            if encoder is None:
                raise InternalServerError()

            data_bytes = encoder(data)
            data = self.__app.response_class(data_bytes, mimetype=media_type)

        if status is not None:
            data.status_code = status

        if headers:
            data.headers.extend(headers)

        return data

    def __fill_param_from_args(self, params, param_name, param_type, args, arg_name, default, required, multiple, validate):
        if not arg_name:
            arg_name = param_name

        parser = self.__parsers.get(param_type)

        if not parser:
            raise FlaskIOError('Parameter type \'%s\' does not have a parser.' % str(param_type))

        if multiple:
            arg_values = args.getlist(arg_name) or [None]
        else:
            arg_values = [args.get(arg_name)]

        param_values = []
        for arg_value in arg_values:
            if arg_value:
                try:
                    arg_value = parser(param_type, arg_value)
                except:
                    raise ValidationError(ErrorReason.invalid_parameter, arg_name, 'Argument \'%s\' is invalid.' % arg_name)

            if not arg_value:
                if required:
                    raise ValidationError(ErrorReason.required_parameter, arg_name, 'Argument \'%s\' is missing.' % arg_name)

                if default:
                    if callable(default):
                        arg_value = default()
                    else:
                        arg_value = default

            if validate and not validate(arg_name, arg_value):
                raise ValidationError(ErrorReason.invalid_parameter, arg_name, 'Argument \'%s\' is invalid.' % arg_name)

            param_values.append(arg_value)

        if multiple:
            params[param_name] = param_values
        else:
            params[param_name] = param_values[0]

    def __fill_param_from_body(self, params, param_name, param_type, schema, required, validate):
        data = request.get_data()

        if not data and required:
            raise ValidationError(ErrorReason.required_parameter, 'body', 'body data is missing.')

        mimetype = get_best_match_for_content_type(self.__decoders)

        if not mimetype:
            raise NotAcceptable()

        decoder = self.__decoders.get(mimetype)

        try:
            arg_value = decoder(data)
        except:
            raise ValidationError(ErrorReason.invalid_parameter, 'body', 'body data is invalid.')

        if schema:
            result = schema.load(arg_value)
            if result.errors:
                key, value = result.errors.popitem()
                raise ValidationError(ErrorReason.invalid_parameter, key, value[0])
            arg_value = schema.load(arg_value).data

        if type(arg_value) != param_type:
            raise FlaskIOError('Value decoded is not compatible with parameter type.')

        if validate and not validate('body', arg_value):
            raise ValidationError(ErrorReason.invalid_parameter, 'body', 'body data is invalid.')

        params[param_name] = arg_value

    def __marshal(self, data, schema, model=None):
        if model and not isinstance(data, model):
            return data

        many = isinstance(data, list)
        return schema.dump(data, many=many).data

    def __output(self, func):
        def decorator():
            data = func()
            return self.make_response(data)
        return decorator

    def __register_views(self):
        for key in self.__app.view_functions.keys():
            self.__app.view_functions[key] = self.__output(self.__app.view_functions[key])
