from flask import Flask
from flask_admin import Admin

from .index import index_router
from .admin import init_flask_admin


def create_views(app: Flask, admin: Admin):
    app.register_blueprint(index_router)
    init_flask_admin(admin)
