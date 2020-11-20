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
        text_requested = request.form.get('text')
        tag_names = [TAG[i].Name for i in request.form.getlist('tag')]
        return redirect(url_for(
            "index.search",
            text=text_requested,
            tag=tag_names
        ))

    tags_all = [t for t in TAG.select().order_by(TAG.Name)]
    text_requested = request.args.get('text', '').lower().strip()
    tags_names = request.args.getlist('tag')

    # These tags are found by tags
    if not tags_names:
        # If no tags are chosen, searching is done by any tag
        tags_names = [t.Name for t in tags_all]
        by_tags = set(m.id for m in MATERIAL.select())
    else:
        # TODO: Certain tags are selected
        tags_requested = (
            TAG
            .select()
            .where(TAG.Name.in_(tags_names))
        )
        tags_requested_id = [t.id for t in tags_requested]
        # =================================================
        materials_candidate_by_tags = (
            MATERIAL.tags
            .get_through_model()
            .select()
            .distinct()
            .where(
                MATERIAL
                .tags
                .get_through_model()
                .tag_id
                .in_(tags_requested_id)
            )
        )
        by_tags = set()
        for m in materials_candidate_by_tags:
            mat_id = m.material_id
            mat_tags = (
                MATERIAL
                .tags
                .get_through_model()
                .select()
                .where(
                    MATERIAL.tags
                    .get_through_model()
                    .material_id == mat_id
                )
            )
            mat_tags_id = set(m.tag_id for m in mat_tags)

            if set(tags_requested_id).issubset(mat_tags_id):
                by_tags.add(mat_id)
        # =================================================

    # Select materials that are found by text
    materials_candidate_by_desc = (
        MATERIAL
        .select()
        .where(
            MATERIAL.Title.contains(text_requested)
            | MATERIAL.Description.contains(text_requested)
        )
    )
    by_desc = set(m.id for m in materials_candidate_by_desc)

    # Select materials which authors are found
    authors_candidate = (
        USER
        .select()
        .where(
            USER.FullName.contains(text_requested)
        )
    )
    authors_candidate_id = [u.id for u in authors_candidate]
    materials_candidate_by_author = (
        MATERIAL.authors
        .get_through_model()
        .select()
        .where(
            MATERIAL.authors
            .get_through_model()
            .user_id
            .in_(authors_candidate_id)
        )
    )
    by_author = set(m.material_id for m in materials_candidate_by_author)

    # These materials are found
    material_requested = (
        MATERIAL
        .select()
        .where(
            MATERIAL.id.in_(by_tags & (by_desc | by_author))
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
        request_text=text_requested,
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


@index_router.route('/material/<int:material_id>/reviews', methods=['GET', 'POST'])
def material_reviews(material_id=None):
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
        return

    # Retrieving comment page number. It is 1 by default.
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            abort(400, description="The page number can't be less than 1")
            return
    except ValueError:
        abort(404, description='Page is not found')
        return

    # Retrieve reviews on this material
    reviews_all = (REVIEW
                   .select()
                   .join(USER, on=(REVIEW.author == USER.id))
                   .where(REVIEW.reviewed_material == material_id)
                   )

    rating_avg = sum([r.Rating for r in reviews_all])/reviews_all.count()

    # Get the necessary slice
    review_page = reviews_all.paginate(page, current_app.config['REVIEWS_PER_PAGE'])

    # Create pagination
    pagination = Pagination(
        per_page=current_app.config['COMMENTS_PER_PAGE'],
        total=reviews_all.count(),
        page=page,
        bs_version=4,
        record_name='Comments',
        alignment='center'
    )

    return render_template('material_reviews.html',
                           material=material,
                           reviews=review_page,
                           pagination=pagination,
                           page=page,
                           reviews_per_page=current_app.config["REVIEWS_PER_PAGE"],
                           rating_avg=rating_avg)
