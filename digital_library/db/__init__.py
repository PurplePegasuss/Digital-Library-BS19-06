from flask_login import UserMixin
from peewee import *
from flask_admin.contrib.peewee import ModelView
from playhouse.flask_utils import FlaskDB
from playhouse.hybrid import hybrid_property
from playhouse.sqlite_ext import *

from digital_library.app import app, admin

db_wrapper = FlaskDB(app)
database = db_wrapper.database


# TODO: add types validation


class BaseModel(db_wrapper.Model):
    admin_view = ModelView


# `id` field is created by peewee


class TAG(BaseModel):
    Name = TextField(unique=True)


class USER(BaseModel, UserMixin):  # if a method is implemented in BaseModel then this method is used
    Email = TextField(unique=True)
    FirstName = TextField()
    SecondName = TextField()
    # an invalid hash by default; can't be compared to anything
    PasswordHash = TextField(default='#')

    @hybrid_property
    def FullName(self):
        return self.FirstName + ' ' + self.SecondName

    def get_id(self):
        return str(self.id)


class MATERIAL(BaseModel):
    Type = TextField()
    Title = TextField(default='')
    # available types for now: educational
    Description = TextField(default='')
    tags = ManyToManyField(TAG, backref='materials')  # TAGGED_WITH
    authors = ManyToManyField(
        USER, backref='suggested_materials')  # SUGGESTED_BY


class COMMENT(BaseModel):
    Text = TextField()
    commented_material = ForeignKeyField(
        MATERIAL, backref='comments')  # COMMENTED_WITH
    author = ForeignKeyField(USER, backref='comments')  # PROVIDED_BY__COMMENT


class ATTACHMENT(BaseModel):
    Type = TextField()
    # available types for now: image,text,file,video,code
    Url = TextField(unique=True)
    material = ForeignKeyField(
        MATERIAL, backref='attachments')  # WITH_ATTACHMENT


class REVIEW(BaseModel):
    Text = TextField()
    Rating = IntegerField()
    reviewed_material = ForeignKeyField(
        MATERIAL, backref='reviews')  # REVIEWED_WITH
    author = ForeignKeyField(USER, backref='reviews')  # PROVIDED_BY__REVIEW


class ADMIN_RIGHTS(BaseModel):
    Description = TextField(unique=True)
    users = ManyToManyField(USER, backref='rights')


class MATERIAL_AdminView(ModelView):
    inline_models = (ATTACHMENT, COMMENT, REVIEW)


MATERIAL.admin_view = MATERIAL_AdminView

tables = [
    TAG,
    USER,
    MATERIAL,
    MATERIAL.tags.get_through_model(),
    MATERIAL.authors.get_through_model(),
    COMMENT,
    ATTACHMENT,
    REVIEW,
    ADMIN_RIGHTS,
    ADMIN_RIGHTS.users.get_through_model(),
]


def init_flask_admin():
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


def create_tables():
    with database:
        database.create_tables(tables)


create_tables()

init_flask_admin()
