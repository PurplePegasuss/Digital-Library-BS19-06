from flask import Blueprint, render_template, current_app, request, abort, redirect, url_for
from flask_paginate import Pagination
from digital_library.db import *

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    # Retrieving material page number. It is 1 by default.
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            abort(400, description="The page number can't be less than 1")
    except ValueError:
        abort(404, description='Page is not found')

    # Retrieve all the materials
    material_all = (
        MATERIAL
        .select()
        .prefetch(MATERIAL.tags.get_through_model(),
                  MATERIAL.authors.get_through_model())
    )

    # Extract the necessary slice
    per_page = current_app.config['MATERIALS_PER_PAGE']
    material_page = material_all[(page - 1)*per_page:page*per_page]

    # Create pagination
    pagination = Pagination(
        per_page=per_page,
        total=len(material_all),
        page=page,
        bs_version=4,
        record_name='Materials',
        alignment='center'
    )

    return render_template('index.html',
                           materials=material_page,
                           pagination=pagination,
                           page=page)


@index_router.route('/search', methods=['GET', 'POST'])
def search():
    # If a user presses the search button
    if request.method == 'POST':
        text = request.form.get('text')

        tag_ids = request.form.getlist('tag')
        tag_names = [TAG[i].Name for i in tag_ids]

        return redirect(url_for(
            "index.search",
            text=text,
            tag=tag_names
        ))

    tags_all = [t for t in TAG.select().order_by(TAG.Name)]

    text = request.args.get('text', '').lower().strip()
    tags_names = request.args.getlist('tag')

    # If no tags are chosen, searching is done by any tag
    if not tags_names:
        tags_names = [t.Name for t in tags_all]

    # These tags are selected by user
    candidate_tags = (
        TAG
        .select()
        .where(TAG.Name.in_(tags_names))
    )

    # These materials contain "Text"
    candidate_by_desc_materials = (
        MATERIAL
        .select()
        .where(
            MATERIAL.Title.contains(text) |
            MATERIAL.Description.contains(text)
        )
    )

    candidate_users = (
        USER
        .select()
        .where(
            USER.FullName.contains(text)
        )
    )

    candidate_tags_id = [t.id for t in candidate_tags]
    candidate_users_id = [u.id for u in candidate_users]

    # These materials have candidate authors
    candidates_by_author = (
        MATERIAL.authors
        .get_through_model()
        .select()
        .where(
            MATERIAL.authors
            .get_through_model()
            .user_id
            .in_(candidate_users_id)
        )
    )

    # TODO: 'MATERIAL.tags' should be a subset of 'candidate_tags_id', not just in_
    # These materials have selected tags
    candidates_by_tag = (
        MATERIAL.tags
        .get_through_model()
        .select()
        .where(
            MATERIAL.tags
            .get_through_model()
            .tag_id
            .in_(candidate_tags_id)
        )
    )

    # "Text" is found in the title/description of a material
    candidate_materials_1_id = set(m.id for m in candidate_by_desc_materials)

    # "Text" is found in authors' FullName
    candidate_materials_2_id = set(m.material_id for m in candidates_by_author)

    # Those tags are selected
    candidate_materials_3_id = set(m.material_id for m in candidates_by_tag)

    # These materials are found
    materials_requested_id = (
        candidate_materials_3_id &
        (candidate_materials_1_id | candidate_materials_2_id)
    )
    material_requested = (
        MATERIAL
        .select()
        .where(
            MATERIAL.id.in_(materials_requested_id)
        )
        .prefetch(
            MATERIAL.tags.get_through_model(),
            MATERIAL.authors.get_through_model()
        )
    )

    # Retrieving material page number. It is 1 by default.
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            abort(400, description="The page number can't be less than 1")
    except ValueError:
        abort(404, description='Page is not found')

    # Extract the necessary slice
    per_page = current_app.config['MATERIALS_PER_PAGE']
    material_page = material_requested[(page - 1) * per_page:page * per_page]

    # Create pagination
    pagination = Pagination(
        per_page=per_page,
        total=len(material_requested),
        page=page,
        bs_version=4,
        record_name='Materials',
        alignment='center'
    )

    return render_template(
        'search.html',
        tags_all=tags_all,
        materials=material_page,
        pagination=pagination,
        page=page,
        request_text=text,
        request_tags=tags_names
    )


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
        total=comments_all.count(),
        page=page,
        bs_version=4,
        record_name='Comments',
        alignment='center'
    )

    return render_template('material.html',
                           material=material,
                           comments=comment_page,
                           pagination=pagination,
                           page=page,
                           comments_per_page=current_app.config["COMMENTS_PER_PAGE"])
