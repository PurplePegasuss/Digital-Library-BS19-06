from hashlib import sha512
from peewee import prefetch

from .app import app
from .db import USER, database
from flask_login import LoginManager, login_user, logout_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

from flask import request, render_template, redirect, url_for, Blueprint, abort

login_manager = LoginManager()
login_manager.init_app(app=app)

auth_router = Blueprint('auth', __name__, template_folder='templates')


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


@auth_router.route('/login', methods=['GET', 'POST'])
def validate_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            login(email, password)
            return redirect(url_for('index.index'))
        except AuthException as e:
            abort(400, description=str(e))

    return render_template('login.html', form=form)


@auth_router.route('/register', methods=['GET', 'POST'])
def validate_register():
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        second_name = form.second_name.data
        email = form.email.data
        password = form.password.data
        try:
            register(email, password, first_name, second_name)
        except AuthException as e:
            abort(400, description=str(e))

    return render_template('register.html', form=form)


def login(email: str, password: str) -> USER:
    password_hash = _hash_password(password)
    user = USER.get_or_none((USER.Email == email) & (USER.PasswordHash == password_hash))

    if user is None:
        raise InvalidCredentialsException()

    login_user(user)

    return user


def logout():
    logout_user()


def register(email: str, password: str, first_name: str = "anon", second_name: str = "anon") -> USER:
    if_exists = USER.select().where(USER.Email == email).exists()
    if if_exists:
        raise AlreadyExistException()

    with database.atomic() as transaction:
        user = USER.create(Email=email, FirstName=first_name, SecondName=second_name,
                           PasswordHash=_hash_password(password))

    login_user(user)

    return user