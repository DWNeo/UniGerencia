from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired

from app.locale import obrigatorio

# Formulário para cadastro de uma mensagem
class PostForm(FlaskForm):
    
    titulo = StringField('Título', validators=[
        DataRequired(message=obrigatorio)])
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message=obrigatorio)])
    
    submit = SubmitField('Postar')

# Formulário para atualização de uma mensagem
class AtualizaPostForm(FlaskForm):
    
    titulo = StringField('Título', validators=[
        DataRequired(message=obrigatorio)])
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message=obrigatorio)])
    
    submit = SubmitField('Postar')