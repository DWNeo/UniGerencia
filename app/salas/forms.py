from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Sala


class SalaForm(FlaskForm):

    numero = StringField('Número', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    setor = StringField('Setor', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    qtd_aluno = StringField('Quantidade de Alunos', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=10, message='Este campo só pode ter até 10 caracteres.')])
    
    submit = SubmitField('Cadastrar')

    def validate_numero(self, numero):
        sala = Sala.query.filter_by(numero=numero.data).first()
        if sala:
            raise ValidationError('Já existe uma sala com esse número.\
                Por favor, insira um diferente.')

class AtualizaSalaForm(FlaskForm):
    
    setor = StringField('Setor', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    qtd_aluno = StringField('Quantidade de Alunos', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=10, message='Este campo só pode ter até 10 caracteres.')])
    status = SelectField('Status', choices=[
        ('Disponível', 'Disponível'), ('Em Uso', 'Em Uso'), 
        ('Debilitada', 'Debilitada'), ('Em Reforma', 'Em Reforma'), 
        ('Indisponível', 'Indisponível')])
    submit = SubmitField('Atualizar')