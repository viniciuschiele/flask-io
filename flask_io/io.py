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
from functools import partial
from inspect import isclass
from marshmallow import fields, Schema
from marshmallow.utils import missing
from uuid import uuid4
from werkzeug.exceptions import InternalServerError, HTTPException, NotAcceptable
from .encoders import register_default_decoders, register_default_encoders
from .errors import ErrorResult, ErrorResultSchema
from .utils import get_best_match_for_content_type, get_func_name, get_request_params
from .utils import convert_validation_errors, http_status_message, marshal, unpack


class FlaskIO(object):
    default_encoder = None

    def __init__(self, app=None):
        self.__app = None
        self.__decoders = {}
        self.__encoders = {}
        self.__marshal_by_func = {}
        self.__params_by_func = {}
        self.__schemas_by_func = {}
        self.__sources = {
            'body': lambda n, m: self.__decode_data(request.data),
            'cookie': lambda n, m: get_request_params(request.cookies, n, m),
            'form': lambda n, m: get_request_params(request.form, n, m),
            'header': lambda n, m: get_request_params(request.headers, n, m),
            'query': lambda n, m: get_request_params(request.args, n, m)
        }

        register_default_decoders(self)
        register_default_encoders(self)

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.__app = app
        self.__app.before_first_request(self.__register_views)
        self.__app.handle_exception = partial(self.__error_router, app.handle_exception)
        self.__app.handle_user_exception = partial(self.__error_router, app.handle_user_exception)

    def bad_request(self, errors):
        error = marshal(ErrorResult(400, errors), ErrorResultSchema())
        return self.make_response((error, 400))

    def conflict(self, errors):
        error = marshal(ErrorResult(409, errors), ErrorResultSchema())
        return self.make_response((error, 409))

    def no_content(self):
        return self.make_response(None)

    def not_found(self, errors):
        error = marshal(ErrorResult(404, errors), ErrorResultSchema())
        return self.make_response((error, 404))

    def ok(self, data, schema=None, envelope=None):
        data = marshal(data, schema, envelope)
        return self.make_response(data)

    def unauthorized(self, errors):
        error = marshal(ErrorResult(401, errors), ErrorResultSchema())
        return self.make_response((error, 401))

    def from_body(self, param_name, schema=None):
        schema = schema() if isclass(schema) else schema

        def wrapper(func):
            self.__register_parameter(func, param_name, schema, 'body')
            return func
        return wrapper

    def from_cookie(self, param_name, field):
        def wrapper(func):
            self.__register_parameter(func, param_name, field, 'cookie')
            return func
        return wrapper

    def from_form(self, param_name, field):
        def wrapper(func):
            self.__register_parameter(func, param_name, field, 'form')
            return func
        return wrapper

    def from_header(self, param_name, field):
        def wrapper(func):
            self.__register_parameter(func, param_name, field, 'header')
            return func
        return wrapper

    def from_query(self, param_name, field=None):
        def wrapper(func):
            self.__register_parameter(func, param_name, field, 'query')
            return func
        return wrapper

    def marshal_with(self, schema, envelope=None):
        schema = schema() if isclass(schema) else schema

        def wrapper(func):
            self.__register_marshal(func, schema, envelope)
            return func
        return wrapper

    def make_response(self, data):
        status = headers = None
        if isinstance(data, tuple):
            data, status, headers = unpack(data)

        if not isinstance(data, self.__app.response_class):
            media_type = request.accept_mimetypes.best_match(self.__encoders, default=self.default_encoder)
            encoder = self.__encoders.get(media_type)

            if encoder is None:
                raise InternalServerError()

            if status is None:
                status = 200 if data is not None else 204

            if data is None:
                data_bytes = None
            else:
                data_bytes = encoder(data)

            data = self.__app.response_class(data_bytes, mimetype=media_type)

        if status is not None:
            data.status_code = status

        if headers:
            data.headers.extend(headers)

        return data

    def register_decoder(self, media_type, func):
        self.__decoders[media_type] = func

    def register_encoder(self, media_type, func):
        if not self.default_encoder:
            self.default_encoder = media_type
        self.__encoders[media_type] = func

    def __decode_data(self, data):
        if not data:
            return None

        mimetype = get_best_match_for_content_type(self.__decoders)

        if not mimetype:
            raise NotAcceptable()

        decoder = self.__decoders.get(mimetype)

        return decoder(data)

    def __get_param_values(self, params):
        data = {}
        for param_name, field_or_schema, location in params:
            multiple = isinstance(field_or_schema, fields.List)
            value = self.__sources[location](param_name, multiple)
            if value is not None and value != '':
                data[param_name] = value
        return data

    def __get_schema_by_func(self, func_name, params):
        schema = self.__schemas_by_func.get(func_name)

        if not schema:
            attrs = {}
            for param_name, field_or_schema, _ in params:
                if isinstance(field_or_schema, Schema):
                    field_or_schema = fields.Nested(field_or_schema, required=True)
                attrs[param_name] = field_or_schema
            schema = self.__schemas_by_func[func_name] = type('IOSchema' + str(uuid4()), (Schema,), attrs)()

        return schema

    def __process_func(self, func):
        def decorator(**kwargs):
            func_name = get_func_name(func)

            params = self.__params_by_func.get(func_name)

            if params:
                schema = self.__get_schema_by_func(func_name, params)
                values = self.__get_param_values(params)
                data, errors = schema.load(values)

                if errors:
                    return self.bad_request(convert_validation_errors(errors, params))

                kwargs.update(data)

            resp = func(**kwargs)

            if resp and not isinstance(resp, self.__app.response_class):
                schema, envelope = self.__marshal_by_func.get(get_func_name(func)) or (None, None)
                if schema:
                    resp = marshal(resp, schema, envelope)

            return self.make_response(resp)
        return decorator

    def __register_parameter(self, func, param_name, field_or_schema, location):
        field_or_schema = field_or_schema or fields.Raw()
        func_name = get_func_name(func)

        params = self.__params_by_func.get(func_name)
        if params is None:
            params = self.__params_by_func[func_name] = []

        if isinstance(field_or_schema, fields.Field):
            field_or_schema.allow_none = True
            if field_or_schema.missing == missing:
                field_or_schema.missing = None

            if field_or_schema.attribute:
                old_param_name = param_name
                param_name = field_or_schema.attribute
                field_or_schema.attribute = old_param_name

        params.append((param_name, field_or_schema, location))

    def __register_marshal(self, func, schema, envelope):
        func_name = get_func_name(func)
        self.__marshal_by_func[func_name] = (schema, envelope)

    def __register_views(self):
        for key in self.__app.view_functions.keys():
            self.__app.view_functions[key] = self.__process_func(self.__app.view_functions[key])

    def __error_router(self, original_handler, e):
        try:
            return original_handler(e)
        except:
            return self.__handle_error(e)

    def __handle_error(self, e):
        if isinstance(e, HTTPException):
            code = e.code
            message = getattr(e, 'description', http_status_message(code))
        else:
            code = 500

            if self.__app.config.get('DEBUG'):
                message = str(e)
            else:
                message = http_status_message(code)

        error = marshal(ErrorResult(code, message), ErrorResultSchema())

        return self.make_response((error, code))
