from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    
    titulo = StringField('Título', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    submit = SubmitField('Postar')