from flask import Flask
from flask_io import FlaskIO, fields
from datetime import datetime
from example.schemas import UserSchema, PatchUserSchema, UpdateUserSchema

app = Flask(__name__)
app.config['DEBUG'] = True

io = FlaskIO()
io.init_app(app)

store = dict()


@app.route('/users', methods=['POST'])
@io.from_body('user', UserSchema)
@io.marshal_with(UserSchema)
def add_user(user):
    if store.get(user.username):
        return io.conflict('User already exists: ' + user.username)

    user.created_at = datetime.now()
    store[user.username] = user
    return user


@app.route('/users')
@io.from_query('username', fields.String())
@io.from_query('max_results', fields.Integer(missing=10))
@io.marshal_with(UserSchema)
def get_users(username, max_results):
    users = list(store.values())

    if username:
        users = [user for user in users if user.username.find(username) > -1]

    return users[:max_results]


@app.route('/users/<username>', methods=['POST'])
@io.from_body('new_user', UpdateUserSchema)
@io.marshal_with(UserSchema)
def update_user(username, new_user):
    user = store.get(username)

    if not user:
        return io.not_found('User not found: ' + username)

    user.first_name = new_user.first_name
    user.last_name = new_user.last_name
    user.email = new_user.email

    return user


@app.route('/users/<username>', methods=['PATCH'])
@io.from_body('new_user', PatchUserSchema)
@io.marshal_with(UserSchema)
def patch_user(username, new_user):
    user = store.get(username)

    if not user:
        return io.not_found('User not found: ' + username)

    user.first_name = new_user.get('first_name', user.first_name)
    user.last_name = new_user.get('last_name', user.last_name)
    user.email = new_user.get('email', user.email)

    return user

if __name__ == '__main__':
    app.run()
