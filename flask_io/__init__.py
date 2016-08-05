# Make marshmallow's functions and classes importable from flask-io
from marshmallow import pre_load, pre_dump, post_load, post_dump, Schema, ValidationError, validates, validates_schema
from marshmallow.utils import missing

from .io import FlaskIO
from .errors import Error
