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

from uuid import uuid4
from flask import request
from functools import wraps
from marshmallow import Schema, fields
from marshmallow.fields import Field
from werkzeug.exceptions import InternalServerError, NotAcceptable
from .encoders import register_default_decoders
from .encoders import register_default_encoders
from .errors import FlaskIOError
from .utils import get_best_match_for_content_type, new_if_isclass, unpack


class FlaskIO(object):
    default_encoder = None

    def __init__(self, app=None):
        self.__app = None
        self.__decoders = {}
        self.__encoders = {}
        self.__parsers = {}
        self.__params_by_func = {}
        self.__schemas_by_func = {}
        self.__sources = {
            'body': self.__decode_body,
            'cookie': lambda: request.cookies,
            'form': lambda: request.form,
            'header': lambda: request.headers,
            'query': lambda: request.args,
        }

        register_default_decoders(self)
        register_default_encoders(self)

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

    def from_body(self, param_name, schema):
        schema = new_if_isclass(schema)

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

    def from_query(self, param_name, field):
        def wrapper(func):
            self.__register_parameter(func, param_name, field, 'query')
            return func
        return wrapper

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

    def __decode_body(self):
        data = request.data
        if not data:
            return None

        mimetype = get_best_match_for_content_type(self.__decoders)

        if not mimetype:
            raise NotAcceptable()

        decoder = self.__decoders.get(mimetype)

        return decoder(data)

    def __marshal(self, data, schema, model=None):
        if model and not isinstance(data, model):
            return data

        many = isinstance(data, list)
        return schema.dump(data, many=many).data

    def __process_func(self, func):
        def decorator():
            try:
                params = self.__params_by_func.get(func)

                if params:
                    schema = self.__get_schema_by_func(func, params)

                    data = self.__retrieve_param_values(params)

                    data, errors = schema.load(data)

                    if errors:
                        self.__bad_request_from_validation(errors)

                    resp = func(**data)
                else:
                    resp = func()

                return self.make_response(resp)
            except Exception as e:
                print(str(e))
                raise

        return decorator

    def __get_schema_by_func(self, func, params):
        schema = self.__schemas_by_func.get(func)

        if not schema:
            attrs = {}
            for param_name, field_or_schema, _ in params:
                if isinstance(field_or_schema, Schema):
                    field_or_schema = fields.Nested(field_or_schema)
                attrs[param_name] = field_or_schema
            schema = self.__schemas_by_func[func] = type('IOSchema' + str(uuid4()), (Schema,), attrs)()

        return schema

    def __bad_request_from_validation(self, errors):
        items = []

        for field, error in errors.items():
            if isinstance(error, list):
                error = error[0]

            if isinstance(error, str):
                error = {'message': error}

            items.append(error)

        raise FlaskIOError(400, items)

    def __retrieve_param_values(self, params):
        data = {}
        for param_name, field_or_schema, location in params:
            values = self.__sources[location]()

            if isinstance(field_or_schema, Schema):
                value = values
            else:
                if isinstance(field_or_schema, fields.List):
                    value = values.getlist(param_name)
                else:
                    value = values.get(param_name)

            if value is not None:
                data[param_name] = value
        return data

    def __register_parameter(self, func, param_name, field_or_schema, location):
        params = self.__params_by_func.get(func)
        if params is None:
            self.__params_by_func[func] = params = []

        if isinstance(field_or_schema, Field) and field_or_schema.attribute:
            old_param_name = param_name
            param_name = field_or_schema.attribute
            field_or_schema.attribute = old_param_name

        params.append((param_name, field_or_schema, location))

    def __register_views(self):
        for key in self.__app.view_functions.keys():
            self.__app.view_functions[key] = self.__process_func(self.__app.view_functions[key])
