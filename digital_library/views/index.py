from flask import Blueprint, render_template, current_app, request, abort
from flask_paginate import Pagination

from digital_library.db import *

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    try:
        page = int(request.args.get('page', 0))
        if page < 0:
            abort(400, description="The page can't be less than 0")
    except ValueError:
        abort(404, description='Page is not found')

    materials = (
        MATERIAL
        .select()
        .paginate(page, current_app.config['MATERIALS_PER_PAGE'])
        .prefetch(MATERIAL.tags.get_through_model(),
                  MATERIAL.authors.get_through_model())
    )

    return render_template('index.html', materials=materials, page=page)


@index_router.errorhandler(404)
def page_not_found(message):
    return render_template('handler404.html', data=message), 404


@index_router.route('/material/<int:material_id>')
def material_overview(material_id=None):
    if (material_id is None) or (not MATERIAL.select().where(MATERIAL.id == material_id).exists()):
        abort(404, "No such material exists!")

    try:
        # Retrieve the material from DB
        # This object can be used in templates as material.<attribute_name>
        material = (MATERIAL
                    .select()
                    .where(MATERIAL.id == material_id)
                    .prefetch(ATTACHMENT,
                              MATERIAL.tags.get_through_model(),
                              MATERIAL.authors.get_through_model(),
                              REVIEW
                              )
                    )[0]
    except (MATERIAL.DoesNotExist, IndexError):
        abort(404, "No such material exists!")

    # Retrieving comment page number. It is 1 by default.
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            abort(400, description="The page number can't be less than 1")
            return
    except ValueError:
        abort(404, description='Page is not found')
        return

    # Retrieve the material
    material = MATERIAL.get_by_id(material_id)

    # Retrieve comments on this material
    comments_all = (COMMENT
                    .select()
                    .where(COMMENT.commented_material == material_id)
                    )

    # Get the necessary slice
    comment_page = comments_all.paginate(page, current_app.config['COMMENTS_PER_PAGE'])

    # Create pagination
    pagination = Pagination(
        per_page=current_app.config['COMMENTS_PER_PAGE'],
        total=len(comments_all),
        page=page,
        record_name='Comments'
    )

    return render_template('material.html',
                           material=material,
                           comments=comment_page,
                           pagination=pagination,
                           bs_version=4,
                           page=page,
                           comments_per_page=current_app.config["COMMENTS_PER_PAGE"])
