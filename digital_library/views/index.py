from flask import Blueprint, render_template, current_app, request, abort

from digital_library.db import MATERIAL

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    try:
        page = int(request.args.get('page', 0))
        if page < 0:
            abort(400, description="The page can't be less than 0")
            return
    except ValueError:
        abort(404, description='Page is not found')
        return

    materials = (MATERIAL
                 .select()
                 .join(MATERIAL.tags.get_through_model())
                 .switch(MATERIAL)
                 .join(MATERIAL.authors.get_through_model())
                 .paginate(page, current_app.config['MATERIALS_PER_PAGE'])
                 )

    return render_template('index.html', materials=materials, hello='world')
