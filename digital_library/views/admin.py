from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView

from ..db import tables
from digital_library.db import ADMIN_RIGHTS, ATTACHMENT, COMMENT, MATERIAL, REVIEW

class MATERIAL_AdminView(ModelView):
    inline_models = (ATTACHMENT, COMMENT, REVIEW)


MATERIAL.admin_view = MATERIAL_AdminView


def init_flask_admin(admin: Admin):
    admin_views = [
        x.admin_view(x) for x in tables if getattr(x, 'admin_view', None)
    ]
    admin_views.extend([
        ModelView(MATERIAL.tags.get_through_model()),
        ModelView(MATERIAL.authors.get_through_model()),
        ModelView(ADMIN_RIGHTS.users.get_through_model()),
    ])
    for view in admin_views:
        admin.add_view(view)
