from flask_io import fields, post_load, validate, Schema
from .models import User


class UserSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(5, 30))
    first_name = fields.String(required=True, validate=validate.Length(1, 50))
    last_name = fields.String(required=True, validate=validate.Length(1, 50))
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_object(self, data):
        return User(**data)


class UpdateUserSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(1, 50))
    last_name = fields.String(required=True, validate=validate.Length(1, 50))
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)

    @post_load
    def make_object(self, data):
        return User(**data)


class PatchUserSchema(Schema):
    first_name = fields.String(validate=validate.Length(1, 50))
    last_name = fields.String(validate=validate.Length(1, 50))
    email = fields.Email()
    enabled = fields.Boolean()
