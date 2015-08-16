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
from marshmallow import fields
from werkzeug.exceptions import InternalServerError, HTTPException, NotAcceptable
from .actions import ActionContext
from .encoders import register_default_decoders, register_default_encoders
from .errors import ErrorResult, ErrorResultSchema
from .utils import get_best_match_for_content_type, get_func_name, get_request_params
from .utils import convert_validation_errors, http_status_message, marshal, unpack


class FlaskIO(object):
    default_encoder = None

    def __init__(self, app=None):
        self.__app = None
        self.__actions = {}
        self.__decoders = {}
        self.__encoders = {}
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
        self.__app.before_first_request(self.__wrap_views)
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
            self.__get_action(func).add_parameter(param_name, schema, 'body')
            return func
        return wrapper

    def from_cookie(self, param_name, field):
        def wrapper(func):
            self.__get_action(func).add_parameter(param_name, field, 'cookie')
            return func
        return wrapper

    def from_form(self, param_name, field):
        def wrapper(func):
            self.__get_action(func).add_parameter(param_name, field, 'form')
            return func
        return wrapper

    def from_header(self, param_name, field):
        def wrapper(func):
            self.__get_action(func).add_parameter(param_name, field, 'header')
            return func
        return wrapper

    def from_query(self, param_name, field=None):
        def wrapper(func):
            self.__get_action(func).add_parameter(param_name, field, 'query')
            return func
        return wrapper

    def marshal_with(self, schema, envelope=None):
        schema = schema() if isclass(schema) else schema

        def wrapper(func):
            action = self.__get_action(func)
            action.output_schema = schema
            action.output_envelope = envelope
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

    def __get_action(self, func):
        func_name = get_func_name(func)

        action = self.__actions.get(func_name)

        if not action:
            action = self.__actions[func_name] = ActionContext()

        return action

    def __get_param_values(self, params):
        data = {}
        for param_name, field_or_schema, location in params:
            multiple = isinstance(field_or_schema, fields.List)
            value = self.__sources[location](param_name, multiple)
            if value is not None and value != '':
                data[param_name] = value
        return data

    def __process_action(self, func):
        def decorator(**kwargs):
            action = self.__get_action(func)

            if action.params:
                values = self.__get_param_values(action.params)
                data, errors = action.input_schema.load(values)

                if errors:
                    return self.bad_request(convert_validation_errors(errors, action.params))

                kwargs.update(data)

            resp = func(**kwargs)

            if resp and not isinstance(resp, self.__app.response_class):
                if action.output_schema:
                    resp = marshal(resp, action.output_schema, action.output_envelope)

            return self.make_response(resp)
        return decorator

    def __wrap_views(self):
        for key in self.__app.view_functions.keys():
            self.__app.view_functions[key] = self.__process_action(self.__app.view_functions[key])

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
