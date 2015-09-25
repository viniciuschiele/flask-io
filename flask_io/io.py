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

import logging

from collections import OrderedDict
from flask import request
from inspect import isclass
from marshmallow import fields
from werkzeug.exceptions import InternalServerError, HTTPException, NotAcceptable
from .actions import ActionContext
from .encoders import json_decode, json_encode
from .time import Stopwatch
from .utils import get_best_match_for_content_type, get_func_name, get_request_params, errors_to_dict
from .utils import collect_trace_data, convert_validation_errors, http_status_message, marshal, unpack


class FlaskIO(object):
    default_decoder = 'application/json'
    default_encoder = 'application/json'
    trace_enabled = False

    def __init__(self, app=None):
        self.__app = None
        self.__actions = {}
        self.__sources = {
            'body': lambda n, m: self.__decode_data(request.data),
            'cookie': lambda n, m: get_request_params(request.cookies, n, m),
            'form': lambda n, m: get_request_params(request.form, n, m),
            'header': lambda n, m: get_request_params(request.headers, n, m),
            'query': lambda n, m: get_request_params(request.args, n, m)
        }

        self.__trace_data_handler = None
        self.__trace_output_handler = self.__write_trace_data

        self.decoders = OrderedDict([('application/json', json_decode)])
        self.encoders = OrderedDict([('application/json', json_encode)])

        self.logger = logging.getLogger('flask-io')

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.__app = app
        self.__app.before_first_request(self.__wrap_views)

        self.trace_enabled = self.__app.config.get('TRACE_ENABLED', self.trace_enabled)

    def bad_request(self, errors):
        return self.make_response((errors_to_dict(errors), 400))

    def conflict(self, errors):
        return self.make_response((errors_to_dict(errors), 409))

    def no_content(self):
        return self.make_response(None)

    def not_found(self, errors):
        return self.make_response((errors_to_dict(errors), 404))

    def ok(self, data, schema=None, envelope=None):
        data = marshal(data, schema, envelope)
        return self.make_response(data)

    def unauthorized(self, errors):
        return self.make_response((errors_to_dict(errors), 401))

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

        if data is None:
            data = self.__app.response_class(status=204)
        elif not isinstance(data, self.__app.response_class):
            media_type = request.accept_mimetypes.best_match(self.encoders, default=self.default_encoder)
            encoder = self.encoders.get(media_type)

            if encoder is None:
                raise InternalServerError()

            data_bytes = encoder(data)

            data = self.__app.response_class(data_bytes, mimetype=media_type)

        if status is not None:
            data.status_code = status

        if headers:
            data.headers.extend(headers)

        return data

    def decoder(self, media_type):
        def wrapper(func):
            self.decoders[media_type] = func
            return func
        return wrapper

    def encoder(self, media_type):
        def wrapper(func):
            self.encoders[media_type] = func
            return func
        return wrapper

    def trace(self):
        def wrapper(func):
            action = self.__get_action(func)
            action.trace_enabled = True
            return func
        return wrapper

    def trace_data_handler(self):
        def decorator(f):
            self.__trace_data_handler = f
            return f
        return decorator

    def trace_output_handler(self):
        def decorator(f):
            self.__trace_output_handler = f
            return f
        return decorator

    def __decode_data(self, data):
        if not data:
            return None

        mimetype = get_best_match_for_content_type(self.decoders, self.default_decoder)

        if not mimetype:
            raise NotAcceptable('Content-Type is not supported: ' + request.headers['content-type'])

        decoder = self.decoders.get(mimetype)

        return decoder(data)

    def __get_action(self, func):
        func_name = get_func_name(func)

        action = self.__actions.get(func_name)

        if not action:
            action = self.__actions[func_name] = ActionContext(func_name)

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
        action = self.__get_action(func)

        def decorator(**kwargs):
            latency_total = Stopwatch.start_new()
            latency_func = Stopwatch()
            response = error = None

            try:
                if action.params:
                    values = self.__get_param_values(action.params)
                    data, errors = action.input_schema.load(values)

                    if errors:
                        return self.bad_request(convert_validation_errors(errors, action.params))

                    kwargs.update(data)

                try:
                    latency_func.start()
                    ret = func(**kwargs)
                finally:
                    latency_func.stop()

                if not isinstance(ret, self.__app.response_class):
                    if action.output_schema:
                        ret = marshal(ret, action.output_schema, action.output_envelope)

                response = self.make_response(ret)
                return response
            except Exception as e:
                error = e
                return self.__handle_error(e)
            finally:
                if action.trace_enabled and self.trace_enabled:
                    latency_total.stop()
                    data = collect_trace_data(action, latency_total, latency_func, error, response)
                    if self.__trace_data_handler:
                        self.__trace_data_handler(data)
                    self.__trace_output_handler(data)

        return decorator

    def __wrap_views(self):
        for key in self.__app.view_functions.keys():
            self.__app.view_functions[key] = self.__process_action(self.__app.view_functions[key])

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

            self.logger.error(str(e))

        error = errors_to_dict(message)

        return self.make_response((error, code))

    def __write_trace_data(self, data):
        message = ''

        for key, value in data.items():
            message += key + ': ' + str(value) + '\r\n'

        self.logger.info(message)
