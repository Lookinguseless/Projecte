from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields import BooleanField, SubmitField
from wtforms.validators import DataRequired


class AddingForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = StringField('Текст', validators=[DataRequired()])
    comments = BooleanField('Разрешить комментирование', default=True)
    submit = SubmitField('Создать')