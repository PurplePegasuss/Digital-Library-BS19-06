from flask import redirect, url_for, abort, render_template, Blueprint
from flask_login import login_required, logout_user

from digital_library.auth import LoginForm, login, AuthException, RegisterForm, register

auth_router = Blueprint('auth', __name__, template_folder='templates')


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


@auth_router.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.index'))
