from flask import Blueprint, render_template
from digital_library.db import *

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    return render_template('index.html')


# Author: Roman
@index_router.route('/list_of_materials')
def list_of_materials():
    # TODO: check whether the database is not empty
    # TODO: check whether attributes are not None and handle it

    data = []
    for material in MATERIAL.select():
        material_attributes = {}
        material_attributes['id'] = material.id
        material_attributes['type'] = material.Type
        material_attributes['tags'] = material.tags
        material_attributes['title'] = material.Title
        material_attributes['authors'] = material.authors
        material_attributes['description'] = material.Description

        data.append(material_attributes)

    return render_template('list_of_materials.html', data = data)


# Author: Roman
@index_router.route('/list_of_materials/<material_id>')
def material(material_id = None):
    if material_id is None:
        return render_template('404.html'), 404

    # TODO: if no such material exist then also 404
    # Retrieve the material from DB
    material = MATERIAL.get(id = material_id)

    # Get its attributes
    data = {}
    data['id'] = material.id
    data['type'] = material.Type
    data['tags'] = material.tags
    data['title'] = material.Title
    data['authors'] = material.authors
    data['description'] = material.Description

    return render_template('comment_section.html', data = data)
