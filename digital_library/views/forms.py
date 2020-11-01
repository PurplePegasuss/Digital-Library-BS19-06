from wtforms import StringField, SelectField, FieldList, SubmitField, Form, FormField
from flask_wtf import FlaskForm
from digital_library.db import *


class TagFrom(Form):
    tag = SelectField(
            label='Tag',
            choices=[t.Name for t in TAG.select().order_by(TAG.Name)]
        )


class MaterialSearchForm(FlaskForm):
    MIN_TAGS = 0
    MAX_TAGS = 6
    tag_choices = [t.Name for t in TAG.select().order_by(TAG.Name)]

    material_name = StringField('Material name')
    tags = FieldList(
        FormField(TagFrom),
        min_entries=MIN_TAGS
    )
    submit = SubmitField('Find')
