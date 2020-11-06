from flask import Flask

from digital_library.views.index import index_router
from digital_library.views.auth import auth_router


def create_views(app: Flask):
    app.register_blueprint(index_router)
    app.register_blueprint(auth_router)
