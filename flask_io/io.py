import functools
import traceback

from flask import request
from inspect import isclass
from logging import getLogger
from werkzeug.exceptions import HTTPException
from . import fields, missing, ValidationError
from .actions import Action
from .errors import APIError, BadRequest, NotAcceptable, UnsupportedMediaType
from .negotiation import DefaultContentNegotiation
from .parsers import JSONParser
from .renderers import JSONRenderer
from .tracing import Tracer
from .utils import errors_to_dict, get_fields_from_request, http_status_message, marshal, unpack, \
    validation_error_to_errors, Stopwatch


class FlaskIO(object):
    """
    The class responsible for parsing request into function parameters and deserialize function returns into response.
    """

    def __init__(self, app=None):
        """
        Initializes a new instance.

        :param app: A Flask instance class.
        """

        self.__app = None

        self.content_negotiation = DefaultContentNegotiation()
        self.default_authenticators = []
        self.default_permissions = []
        self.default_parsers = [JSONParser()]
        self.default_renderers = [JSONRenderer()]

        self.logger = getLogger('flask-io')

        self.tracer = Tracer(self)

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize this class with the specified :class:`flask.Flask` application

        :param app: The Flask application.
        """

        self.__app = app
        self.__app.before_first_request(self.__setup)

        self.tracer.enabled = self.__app.config.get('TRACE_ENABLED', self.tracer.enabled)

    def bad_request(self, error):
        """
        Gets a 404 response with the specified error.

        :param error: The error to include in the response.
        :return: A Flask response object.
        """

        return self.__make_response((errors_to_dict(error), 400))

    def conflict(self, error):
        """
        Gets a 409 response with the specified error.

        :param error: The error to include in the response.
        :return: A Flask response object.
        """

        return self.__make_response((errors_to_dict(error), 409))

    def created(self, data, schema=None, envelope=None):
        """
        Gets a 201 response with the specified data.

        :param data: The content value.
        :param schema: The schema to serialize the data.
        :param envelope: The key used to envelope the data.
        :return: A Flask response object.
        """

        data = marshal(data, schema, envelope)
        return self.__make_response((data, 201))

    def forbidden(self, error):
        """
        Gets a 403 response with the specified error.

        :param error: The error to include in the response.
        :return: A Flask response object.
        """

        return self.__make_response((errors_to_dict(error), 403))

    def no_content(self):
        """
        Gets a 204 response with no content.

        :return: A Flask response object.
        """

        return self.__make_response((None, 204))

    def not_found(self, error):
        """
        Gets a 404 response with the specified error.

        :param error: The error to include in the response.
        :return: A Flask response object.
        """

        return self.__make_response((errors_to_dict(error), 404))

    def ok(self, data, schema=None, envelope=None):
        """
        Gets a 200 response with the specified data.

        :param data: The content value.
        :param schema: The schema to serialize the data.
        :param envelope: The key used to envelope the data.
        :return: A Flask response object.
        """

        data = marshal(data, schema, envelope)
        return self.__make_response(data)

    def unauthorized(self, error):
        """
        Gets a 401 response with the specified error.

        :param error: The error to include in the response.
        :return: A Flask response object.
        """
        return self.__make_response((errors_to_dict(error), 401))

    def authenticators(self, auths):
        """
        A decorator that sets a list of authenticators for a function.

        :param auths: The list of authenticator instances or classes.
        :return: A function
        """

        if not isinstance(auths, (list, tuple)):
            auths = [auths]

        instances = []

        for auth in auths:
            if isclass(auth):
                instances.append(auth())
            else:
                instances.append(auth)

        def decorator(func):
            func.authenticators = instances
            return func
        return decorator

    def permissions(self, perms):
        """
        A decorator that sets a list of permissions for a function.

        :param perms: The list of permission instances or classes.
        :return: A function
        """

        if not isinstance(perms, (list, tuple)):
            perms = [perms]

        instances = []

        for perm in perms:
            if isclass(perm):
                instances.append(perm())
            else:
                instances.append(perm)

        def decorator(func):
            func.permissions = instances
            return func
        return decorator

    def from_body(self, param_name, schema):
        """
        A decorator that converts the request body into a function parameter based on the specified schema.

        :param param_name: The parameter which receives the argument.
        :param schema: The schema class or instance used to deserialize the request body toa Python object.
        :return: A function
        """

        schema = schema() if isclass(schema) else schema

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                kwargs[param_name] = self.__parse_body(schema)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def from_cookie(self, param_name, field):
        """
        A decorator that converts a request cookie into a function parameter based on the specified field.

        :param str param_name: The parameter which receives the argument.
        :param Field field: The field class or instance used to deserialize the request cookie to a Python object.
        :return: A function
        """

        return self.__from_source(param_name, field, lambda: request.cookies, 'cookie')

    def from_form(self, param_name, field):
        """
        A decorator that converts a request form into a function parameter based on the specified field.

        :param str param_name: The parameter which receives the argument.
        :param Field field: The field class or instance used to deserialize the request form to a Python object.
        :return: A function
        """
        return self.__from_source(param_name, field, lambda: request.form, 'form')

    def from_header(self, param_name, field):
        """
        A decorator that converts a request header into a function parameter based on the specified field.

        :param str param_name: The parameter which receives the argument.
        :param Field field: The field class or instance used to deserialize the request header to a Python object.
        :return: A function
        """
        return self.__from_source(param_name, field, lambda: request.headers, 'header')

    def from_query(self, param_name, field):
        """
        A decorator that converts a query string into a function parameter based on the specified field.

        :param param_name: The parameter which receives the argument.
        :param Field field: The field class or instance used to deserialize the request query string to a Python object.
        :return: A function
        """

        return self.__from_source(param_name, field, lambda: request.args, 'query')

    def marshal_with(self, schema, envelope=None):
        """
        A decorator that apply marshalling to the return values of your methods.

        :param schema: The schema class to be used to serialize the values.
        :param envelope: The key used to envelope the data.
        :return: A function.
        """

        # schema is pre instantiated to avoid instantiate it
        # on every request
        schema_is_class = isclass(schema)
        schema_cache = schema() if schema_is_class else schema

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                data = func(*args, **kwargs)
                if isinstance(data, self.__app.response_class):
                    return data

                schema_instance = schema_cache

                # if there is the parameter 'fields' in the url
                # we cannot use the cached schema instance
                # in this case we have to instantiate the schema
                # on every request.
                if schema_is_class:
                    only = get_fields_from_request()
                    if only:
                        schema_instance = schema(only=only)

                return marshal(data, schema_instance, envelope)
            return wrapper
        return decorator

    def trace_inspect(self):
        """
        A decorator that allows to inspect/change the trace data.
        """
        def decorator(f):
            self.tracer.inspector = f
            return f
        return decorator

    def trace_emit(self):
        """
        A decorator that allows to change the trace emitter.
        By default Python logging is used to emit the trace data.
        """
        def decorator(f):
            self.tracer.emitter = f
            return f
        return decorator

    def __handle_error(self, e):
        if isinstance(e, ValidationError):
            code = 400
            error = validation_error_to_errors(e)
        elif isinstance(e, APIError):
            code = e.status_code
            error = e.error
        elif isinstance(e, HTTPException):
            code = e.code
            error = getattr(e, 'description', http_status_message(code))
        else:
            code = 500
            error = traceback.format_exc() if self.__app.config.get('DEBUG') else http_status_message(code)
            self.logger.error(traceback.format_exc())

        errors_data = errors_to_dict(error)

        return self.__make_response((errors_data, code), self.default_renderers[0])

    def __make_response(self, data, default_renderer=None):
        """
        Creates a Flask response object from the specified data.
        The appropriated encoder is taken based on the request header Accept.
        If there is not data to be serialized the response status code is 204.

        :param data: The Python object to be serialized.
        :return: A Flask response object.
        """

        status = headers = None
        if isinstance(data, tuple):
            data, status, headers = unpack(data)

        if data is None:
            data = self.__app.response_class(status=204)
        elif not isinstance(data, self.__app.response_class):
            renderer, mimetype = self.content_negotiation.select_renderer(request, self.default_renderers)

            if not renderer:
                if not default_renderer:
                    raise NotAcceptable()

                renderer = default_renderer
                mimetype = default_renderer.mimetype

            data_bytes = renderer.render(data, mimetype)
            data = self.__app.response_class(data_bytes, mimetype=str(mimetype))

        if status is not None:
            data.status_code = status

        if headers:
            data.headers.extend(headers)

        return data

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

            # if the missing attribute is not None
            # it will return the value without deserializing it.
            if raw_value is not missing:
                return raw_value

            if not field.required:
                raw_value = None

        try:
            return field.deserialize(raw_value, field_name, data)
        except ValidationError as e:
            e.messages = {field_name: e.messages}
            e.kwargs['location'] = location
            raise

    def __parse_body(self, schema):
        if not request.get_data():
            raise BadRequest('Payload missing.')

        parser, mimetype = self.content_negotiation.select_parser(request, self.default_parsers)

        if not parser:
            raise UnsupportedMediaType(request.headers['content-type'])

        try:
            decoded_data = parser.parse(request.get_data(), mimetype)
        except:
            raise BadRequest('Malformed request.')

        model, errors = schema.load(decoded_data)

        if errors:
            raise ValidationError(errors, data=request.get_data(), location='body')

        return model

    def __process_action(self, action):
        def decorator(**kwargs):
            latency = response = error = None

            if action.trace_enabled and self.tracer.enabled:
                latency = Stopwatch.start_new()

            try:
                response = action(**kwargs)
                response = self.__make_response(response)
                return response
            except Exception as e:
                error = e
                response = self.__handle_error(e)
                return response
            finally:
                if action.trace_enabled and self.tracer.enabled:
                    latency.stop()
                    self.tracer.trace(request, response, error, latency)

        return decorator

    def __setup(self):
        for endpoint in self.__app.view_functions.keys():
            for rule in self.__app.url_map.iter_rules(endpoint):
                if self.tracer.match(rule):
                    trace_enabled = True
                    break
            else:
                trace_enabled = False

            action = Action(self.__app.view_functions[endpoint],
                            self.default_authenticators,
                            self.default_permissions,
                            trace_enabled)

            self.__app.view_functions[endpoint] = self.__process_action(action)
