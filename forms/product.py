from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, SubmitField
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class ProductsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    pic = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
