from digital_library.db import *
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length


class CommentForm(FlaskForm):
    text = StringField('Leave your comment', validators=[InputRequired(), Length(max=200)])
