from flask import current_app as app, abort, request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.peewee import ModelView
from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from ..db import tables
from digital_library.db import ADMIN_RIGHTS, ATTACHMENT, COMMENT, MATERIAL, REVIEW


class MATERIAL_AdminView(ModelView):
    inline_models = (ATTACHMENT, COMMENT, REVIEW)


MATERIAL.admin_view = MATERIAL_AdminView


class UploadFormView(BaseView):
    class UploadForm(FlaskForm):
        upload = FileField('Upload new material', validators=[
            FileRequired()
        ])

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        try:
            page = int(request.args.get('page', 1))
            if page < 1:
                abort(400, description="The page number can't be less than 1")
                return
        except ValueError:
            abort(404, description='Page is not found')
            return

        form = UploadFormView.UploadForm()
        files = map(lambda x: x.relative_to(app.static_folder), app.config['UPLOAD_PATH'].iterdir())

        if form.validate_on_submit():
            f = form.upload.data
            fname = secure_filename(f.filename)
            f.save(str(app.config['UPLOAD_PATH'] / fname))

        return self.render('admin/upload.html', form=form, files=files)


def init_flask_admin(admin: Admin):
    admin_views = [
        x.admin_view(x) for x in tables if getattr(x, 'admin_view', None)
    ]
    admin_views.extend([
        UploadFormView(),
        ModelView(MATERIAL.tags.get_through_model()),
        ModelView(MATERIAL.authors.get_through_model()),
        ModelView(ADMIN_RIGHTS.users.get_through_model()),
    ])
    for view in admin_views:
        admin.add_view(view)
