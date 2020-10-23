from flask import Blueprint, jsonify, render_template, abort
from digital_library.db import *

index_router = Blueprint('index', __name__, template_folder = 'templates')


@index_router.route('/')
def index():
    return render_template('index.html')


@index_router.errorhandler(404)
def page_not_found(message):
    return jsonify(error = str(message)), 404


@index_router.route('/list_of_materials')
def list_of_materials():
    # TODO: if database is empty, raise 404 (fix somehow)
    if not MATERIAL.select().exists():
        abort(404, "There are no materials at all!")

    data = []

    for material in MATERIAL.select():
        data.append({
            'id': material.id,
            'type': material.Type,
            'title': material.Title,
            'description': material.Description,
            'tags': [TAG.get_by_id(tag_id).Name for tag_id in material.tags],
            'authors': [USER.get_by_id(user_id).FullName for user_id in material.authors]
        })

    return render_template('list_of_materials.html', data = data)


@index_router.route('/list_of_materials/<material_id>')
def material_overview(material_id = None):
    if material_id is None:
        abort(404, description = "No such material exists!")

    #
    # # If no such material exists, raise 404
    # if not MATERIAL.select().where(id = material_id).exists():
    #     abort(404, description = "No such material exists!")

    # This dictionary is to be sent to the template
    data = {}

    # Retrieve the material from DB
    material = MATERIAL.get(id = material_id)

    # Retrieve its attributes
    data['material_attr'] = {
            'id': material.id,
            'type': material.Type,
            'title': material.Title,
            'description': material.Description,
            'tags': [TAG.get_by_id(tag_id).Name for tag_id in material.tags],
            'authors': [USER.get_by_id(user_id).FullName for user_id in material.authors]
        }

    # Retrieve respective comments
    data['comments'] = []
    for comment in COMMENT.select(COMMENT.commented_material == material_id):
        data['comments'].append({
            'authors': comment.author,
            'text': comment.Text
        })

    # Retrieve respective attachments
    data['attachments'] = []
    for attachment in ATTACHMENT.select(ATTACHMENT.material == material_id):
        data['attachments'].append({
            'type': attachment.Type,
            'urls': [url for url in attachment.URLS]
        })

    return render_template('material.html', data = data)
