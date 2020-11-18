from digital_library.db import *
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length


class CommentForm(FlaskForm):
    text = StringField('text', validators=[InputRequired(), Length(max=200)])
