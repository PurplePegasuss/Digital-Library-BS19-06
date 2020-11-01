from flask import Blueprint, render_template, current_app, request, abort
from flask_paginate import Pagination
from digital_library.views.forms import *
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
def search(add_tag=False, remove_tag=False):
    form = MaterialSearchForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        tags = list(set([t['tag'] for t in form.tags.data]))
        text = form.material_name.data.strip()

        tag_IDs = (
                TAG
                .select(TAG.id)
                .where(TAG.Name.in_(tags))
        )

        print(tags)
        print(tag_IDs)

        materials = (
            MATERIAL
            .select()
            .prefetch(MATERIAL.tags.get_through_model(),
                      MATERIAL.authors.get_through_model())
        )

        results = []
        for material in materials:
            if set([tag.Name for tag in material.tags]) & set(tags) == set(tags):
                if (text.lower() in material.Title.lower()) or (text in material.Description.lower()):
                    results.append(material)

        # tag_IDs = TAG.select(TAG.get_id).where()
        #
        # materials = (
        #     MATERIAL
        #     .select()
        #     .where(MATERIAL.tags.in_())
        # )

        print(tags)

        return render_template("search.html", materials=results, form=form)

    else:
        print('NOOO')

    return render_template('search.html', form=form)


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
