import functools
from hashlib import sha512
from peewee import prefetch

from .app import app
from .cfg import ROOT_PASSWORD
from .db import USER, database, ADMIN_RIGHTS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import abort

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

login_manager = LoginManager()
login_manager.init_app(app=app)


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
    first_name = StringField('first_name', validators=[InputRequired(), Length(min=2, max=50)])
    second_name = StringField('second_name', validators=[InputRequired(), Length(min=2, max=50)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return prefetch(USER
                        .select()
                        .where(USER.id == int(user_id)),
                        USER.rights.get_through_model())[0]
    except (KeyError, ValueError):
        return None


class AuthException(Exception):
    def __init__(self):
        super(Exception, self).__init__("Authentication error!")


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super(Exception, self).__init__("Invalid credentials!")


class AlreadyExistException(AuthException):
    def __init__(self):
        super(Exception, self).__init__("User with given email already exist!")


def _hash_password(password: str) -> str:
    return str(sha512(password.encode("utf-8")).hexdigest())


def login(email: str, password: str) -> USER:
    password_hash = _hash_password(password)
    user = USER.get_or_none((USER.Email == email) & (USER.PasswordHash == password_hash))

    if user is None:
        raise InvalidCredentialsException()

    login_user(user)

    return user


def register(email: str, password: str, first_name: str = "anon", second_name: str = "anon") -> USER:
    if_exists = USER.select().where(USER.Email == email).exists()
    if if_exists:
        raise AlreadyExistException()

    with database.atomic() as transaction:
        user = USER.create(Email=email, FirstName=first_name, SecondName=second_name,
                           PasswordHash=_hash_password(password))

    login_user(user)

    return user


permissions = [
    'ADMIN',
]


def init_permissions():
    with database.atomic():
        root, _ = USER.get_or_create(Email='root@root.root', FirstName='Admin', SecondName='Root',
                                     PasswordHash=_hash_password(ROOT_PASSWORD))
        root.PasswordHash = _hash_password(ROOT_PASSWORD)

        root.rights.clear()
        for permission in permissions:
            right, _ = ADMIN_RIGHTS.get_or_create(Description=permission)
            root.rights.add(right)

        root.save()


init_permissions()


def has_permission(permission: str):
    if not current_user.is_authenticated:
        return False
    return permission in [x.Description for x in current_user.rights]


def permission_required(permission: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if has_permission(permission):
                return func(*args, **kwargs)
            abort(401, 'Unauthorized')

        return wrapper

    return decorator
