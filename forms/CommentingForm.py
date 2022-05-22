from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields import BooleanField, SubmitField
from wtforms.validators import DataRequired


class CommentingForm(FlaskForm):
    content = StringField('Текст', validators=[DataRequired()])
    submit = SubmitField('Создать')