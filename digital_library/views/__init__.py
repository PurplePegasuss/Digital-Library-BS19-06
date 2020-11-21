from flask import Flask, url_for, redirect
from flask_admin import Admin

from .index import index_router
from .admin import init_flask_admin
from .auth import auth_router


def create_views(app: Flask, admin: Admin):
    app.register_blueprint(index_router)
    app.register_blueprint(auth_router)
    init_flask_admin(admin)

    @app.errorhandler(401)
    def unauthorized(message):
        return redirect(url_for('auth.validate_login'))
