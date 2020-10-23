from flask import Blueprint, render_template
from digital_library.db import *

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    return render_template('index.html')


@index_router.route('/list_of_materials')
def list_of_materials():
    # TODO: check whether the database is not empty
    data = [(material.Title, material.id) for material in MATERIAL.select()]
    return render_template('list_of_materials.html', data = data)


@index_router.route('/list_of_materials/<materialId>')
def material(materialId = None):
    # TODO: if no such material exist then also 404
    if materialId is None:
        return render_template('404.html'), 404

    return render_template('comment_section.html')
