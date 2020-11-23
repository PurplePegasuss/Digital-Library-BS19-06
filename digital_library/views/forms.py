from digital_library.db import *
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Length


class CommentForm(FlaskForm):
    text = StringField('Leave your comment', validators=[InputRequired(), Length(max=200)])


class ReviewForm(FlaskForm):
    text = StringField('Leave your review', validators=[InputRequired(), Length(max=200)])
    rating = SelectField('Rating', choices=[(f'{i}', f'{i}') for i in range(1, 11)])
