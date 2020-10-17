from flask import Flask

from digital_library.views.index import index_router


def create_views(app: Flask):
    app.register_blueprint(index_router)
