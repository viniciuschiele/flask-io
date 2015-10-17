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

import functools

from collections import OrderedDict
from flask import request
from inspect import isclass
from logging import getLogger
from werkzeug.exceptions import BadRequest, InternalServerError, HTTPException, UnsupportedMediaType
from . import fields, missing, ValidationError
from .encoders import json_decode, json_encode
from .tracing import Stopwatch, Tracer
from .utils import get_best_match_for_content_type, errors_to_dict
from .utils import http_status_message, marshal, unpack, validation_error_to_errors


class FlaskIO(object):
    default_decoder = 'application/json'
    default_encoder = 'application/json'

    def __init__(self, app=None):
        self.__app = None

        self.decoders = OrderedDict([('application/json', json_decode)])
        self.encoders = OrderedDict([('application/json', json_encode)])

        self.logger = getLogger('flask-io')

        self.tracer = Tracer(self)

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.__app = app
        self.__app.before_first_request(self.__setup)

        self.tracer.enabled = self.__app.config.get('TRACE_ENABLED', self.tracer.enabled)

    def bad_request(self, error):
        return self.make_response((errors_to_dict(error), 400))

    def conflict(self, error):
        return self.make_response((errors_to_dict(error), 409))

    def forbidden(self, error):
        return self.make_response((errors_to_dict(error), 403))

    def no_content(self):
        return self.make_response(None)

    def not_found(self, error):
        return self.make_response((errors_to_dict(error), 404))

    def ok(self, data, schema=None, envelope=None):
        data = marshal(data, schema, envelope)
        return self.make_response(data)

    def unauthorized(self, error):
        return self.make_response((errors_to_dict(error), 401))

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

    def from_body(self, param_name, schema):
        schema = schema() if isclass(schema) else schema

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                kwargs[param_name] = self.__parse_body(schema)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_cookie(self, param_name, field):
        return self.__from_source(param_name, field, lambda: request.cookies, 'cookie')

    def from_form(self, param_name, field):
        return self.__from_source(param_name, field, lambda: request.form, 'form')

    def from_header(self, param_name, field):
        return self.__from_source(param_name, field, lambda: request.headers, 'header')

    def from_query(self, param_name, field):
        return self.__from_source(param_name, field, lambda: request.args, 'query')

    def marshal_with(self, schema, envelope=None):
        schema = schema() if isclass(schema) else schema

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                data = func(*args, **kwargs)
                if isinstance(data, self.__app.response_class):
                    return data
                return marshal(data, schema, envelope)
            return wrapper
        return decorator

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

    def trace_inspect(self):
        def decorator(f):
            self.tracer.inspector = f
            return f
        return decorator

    def trace_emit(self):
        def decorator(f):
            self.tracer.emitter = f
            return f
        return decorator

    def __decode_data(self, data):
        mimetype = get_best_match_for_content_type(self.decoders, self.default_decoder)

        if not mimetype:
            raise UnsupportedMediaType('Content-Type is not supported: ' + request.headers['content-type'])

        decoder = self.decoders.get(mimetype)

        try:
            return decoder(data)
        except:
            raise BadRequest('Invalid payload format.')

    def __from_source(self, param_name, field, getter_data, location):
        field = field() if isclass(field) else field
        if not field.required:
            field.allow_none = True

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                kwargs[param_name] = self.__parse_field(param_name, field, getter_data(), location)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def __handle_error(self, e):
        if isinstance(e, HTTPException):
            code = e.code
            error = getattr(e, 'description', http_status_message(code))
        elif isinstance(e, ValidationError):
            code = 400
            error = validation_error_to_errors(e)
        else:
            code = 500
            error = str(e) if self.__app.config.get('DEBUG') else http_status_message(code)
            self.logger.error(str(e))

        errors = errors_to_dict(error)

        return self.make_response((errors, code))

    def __parse_field(self, field_name, field, data, location):
        field.allow_none = True

        field_name = field.load_from or field_name

        if isinstance(field, fields.List):
            raw_value = data.getlist(field_name) or missing
        else:
            raw_value = data.get(field_name) or missing

        if raw_value is missing:
            missing_value = field.missing
            raw_value = missing_value() if callable(missing_value) else missing_value

        if raw_value is missing and not field.required:
            raw_value = None

        try:
            return field.deserialize(raw_value, field_name, data)
        except ValidationError as e:
            e.messages = {field_name: e.messages}
            e.kwargs['location'] = location
            raise

    def __parse_body(self, schema):
        if not request.data:
            raise BadRequest('Payload is missing.')

        try:
            decoded_data = self.__decode_data(request.data)
        except:
            raise BadRequest('Invalid payload format.')

        model, errors = schema.load(decoded_data)

        if errors:
            raise ValidationError(errors, data=request.data, location='body')

        return model

    def __process_request(self, func, should_trace):
        def decorator(**kwargs):
            latency = response = error = None

            if should_trace and self.tracer.enabled:
                latency = Stopwatch.start_new()

            try:
                response = func(**kwargs)
                response = self.make_response(response)
                return response
            except Exception as e:
                error = e
                response = self.__handle_error(e)
                return response
            finally:
                if should_trace and self.tracer.enabled:
                    latency.stop()
                    self.tracer.trace(request, response, error, latency)

        return decorator

    def __setup(self):
        for endpoint in self.__app.view_functions.keys():
            should_trace = False

            for rule in self.__app.url_map.iter_rules(endpoint):
                if self.tracer.match(rule):
                    should_trace = True
                    break

            self.__app.view_functions[endpoint] = \
                self.__process_request(self.__app.view_functions[endpoint], should_trace)
