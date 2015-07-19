from flask import make_response, request, Response
from functools import wraps
from .encoders import get_default_encoders
from .errors import ErrorReason
from .errors import FlaskIOError
from .errors import MediaTypeSupported
from .errors import ValidationError
from .parsers import get_default_parsers


class FlaskIO(object):
    default_encoder = 'application/json'

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

    def render(self):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.__render(func(*args, **kwargs))
            return wrapper
        return decorator

    def __decode_body_into_param(self, params, param_name, param_type, required, validate):
        data = request.get_data()

        if not data and required:
            raise ValidationError(ErrorReason.required_parameter, 'payload', 'Payload is missing.')

        try:
            if param_type is str:
                arg_value = data.decode()
            else:
                arg_value = self.__get_encoder_from_content_type().decode(data)
        except Exception as e:
            if isinstance(e, MediaTypeSupported):
                raise
            raise ValidationError(ErrorReason.invalid_parameter, 'payload', 'Payload is invalid.')

        if validate:
            try:
                success = validate(arg_value)
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                success = False

            if not success:
                raise ValidationError(ErrorReason.invalid_parameter, 'payload', 'Payload is invalid.')

        params[param_name] = arg_value

    def __get_encoder_from_content_type(self):
        content_type = request.headers['content-type']

        if content_type:
            media_type = content_type.split(';')[0]
        else:
            media_type = FlaskIO.default_encoder

        encoder = self.__encoders.get(media_type)

        if not encoder:
            raise MediaTypeSupported([media_type], 'Media type not supported: %s' % media_type)

        return encoder

    def __get_encoder_from_accept(self):
        accept = request.headers['accept']

        if not accept or '*/*' in accept:
            media_types = [FlaskIO.default_encoder]
        else:
            media_types = accept.split(',')

        encoder = None

        for media_type in media_types:
            encoder = self.__encoders.get(media_type.split(';')[0])
            if encoder:
                break

        if not encoder:
            raise MediaTypeSupported(media_types, 'Media types not supported: %s' % ', '.join(media_types))

        return encoder

    def __parse_arg_into_param(self, params, param_name, param_type, args, arg_name, default, required, multiple, validate):
        if not arg_name:
            arg_name = param_name

        parser = self.__parsers.get(param_type)

        if not parser:
            raise FlaskIOError('Parameter type \'%s\' does not have a parser.' % str(param_type))

        if multiple:
            arg_values = args.getlist(arg_name) or [None]
            param_values = []
            for arg_value in arg_values:
                param_values.append(self.__parse_arg(parser, arg_name, arg_value, default, required, validate))
            params[param_name] = param_values
        else:
            arg_value = args.get(arg_name)
            params[param_name] = self.__parse_arg(parser, arg_name, arg_value, default, required, validate)

    @staticmethod
    def __parse_arg(parser, arg_name, arg_value, default, required, validate):
        try:
            if arg_value:
                arg_value = parser.parse(arg_value)
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

        if validate:
            try:
                success = validate(arg_name, arg_value)
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                success = False

            if not success:
                raise ValidationError(ErrorReason.invalid_parameter, arg_name, 'Argument \'%s\' is invalid.' % arg_name)

        return arg_value

    def __render(self, data):
        status = headers = None
        if isinstance(data, tuple):
            data, status, headers = data + (None,) * (3 - len(data))

        if not isinstance(data, Response):
            encoder = self.__get_encoder_from_accept()

            data_bytes = encoder.encode(data)

            data = Response(data_bytes, mimetype=encoder.mime_type)

        if status is not None:
            if isinstance(status, str):
                data.status = status
            else:
                data.status_code = status

        if headers:
            data.headers.extend(headers)

        return data
