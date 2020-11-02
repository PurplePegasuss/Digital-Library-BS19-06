from hashlib import sha512
from peewee import prefetch

from .app import app
from .db import USER
from flask_login import LoginManager, login_user, logout_user

login_manager = LoginManager()
login_manager.init_app(app=app)


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
        raise AuthException()

    login_user(user)

    return user


def logout():
    logout_user()


def register(email: str, password: str, first_name: str = "anon", second_name: str = "anon") -> USER:
    if_exists = USER.select().where(USER.Email == email).exists()
    if if_exists:
        raise AlreadyExistException()

    with USER.Meta.database.atomic() as transaction:
        user = USER.create(Email=email, FirstName=first_name, SecondName=second_name,
                           PasswordHash=_hash_password(password))

    login_user(user)

    return user
