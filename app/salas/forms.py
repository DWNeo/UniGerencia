from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, IntegerField, TextAreaField, 
                     BooleanField, SelectField)
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange

from app.models import Sala
from app.locale import obrigatorio, max_20, max_50, num_invalido, sala_existente

# Formulário para cadastro de uma nova sala
class SalaForm(FlaskForm):

    numero = StringField('Número', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)])
    setor = SelectField('Setor', validators=[
        DataRequired(message=obrigatorio)], coerce=int)
    qtd_aluno = IntegerField('Quantidade de Alunos', validators=[
        DataRequired(message=obrigatorio), 
        NumberRange(min=1, max=999, message=num_invalido)])
    
    submit = SubmitField('Cadastrar')

    def validate_numero(self, numero):
        sala = Sala.query.filter_by(numero=numero.data).first()
        if sala:
            raise ValidationError(sala_existente)

# Formulário para atualização de um sala
class AtualizaSalaForm(FlaskForm):
    
    setor = SelectField('Setor', validators=[
        DataRequired(message=obrigatorio)], coerce=int)
    qtd_aluno = IntegerField('Quantidade de Alunos', validators=[
        DataRequired(message=obrigatorio), 
        NumberRange(min=1, max=999, message=num_invalido)])
    submit = SubmitField('Atualizar')

# Formulário para indisponibilização um equipamento
class IndisponibilizaSalaForm(FlaskForm):
    
    motivo = TextAreaField('Motivo', validators=[
        DataRequired(message=obrigatorio)])
    submit = SubmitField('Confirmar')

# Formulário para cadastro de um novo relatório da sala
class RelatorioSalaForm(FlaskForm):

    tipo = SelectField('Tipo do Relatório', choices=[
        ('REVISAO', 'Revisão'), ('MANUTENCAO', 'Manutenção'), ('OUTRO', 'Outro')])
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message=obrigatorio)])
    manutencao = BooleanField('Necessita de Manutenção')
    reforma = BooleanField('Necessita de Reforma')
    detalhes = TextAreaField('Detalhes Adicionais')
    submit = SubmitField('Cadastrar')

# Formulário para atualização de um relatório da sala
class AtualizaRelatorioSalaForm(FlaskForm):

    tipo = StringField('Autor', render_kw={'disabled':''})
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message=obrigatorio)])
    manutencao = BooleanField('Necessita de Manutenção', render_kw={'disabled':''})
    reforma = BooleanField('Necessita de Reforma', render_kw={'disabled':''})
    detalhes = TextAreaField('Detalhes Adicionais')
    status = BooleanField('Finalizar')
    submit = SubmitField('Atualizar')

class SetorForm(FlaskForm):
    nome = StringField('Nome', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=50, message=max_50)])
    submit = SubmitField('Cadastrar')