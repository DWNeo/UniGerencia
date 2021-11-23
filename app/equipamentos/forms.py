from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Equipamento, TipoEquipamento


class EquipamentoForm(FlaskForm):

    patrimonio = StringField('Patrimônio', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    descricao = StringField('Descrição', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=50, message='Este campo só pode ter até 50 caracteres.')])
    tipo_eqp = SelectField('Tipo', coerce=int)
    submit = SubmitField('Cadastrar')

    def validate_patrimonio(self, patrimonio):
        equipamento = Equipamento.query.filter_by(
            patrimonio=patrimonio.data).first()
        if equipamento:
            raise ValidationError('Já existe um equipamento com esse\
                patrimônio. Por favor, insira um diferente.')


class AtualizaEquipamentoForm(FlaskForm):

    descricao = StringField('Descrição', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=50, message='Este campo só pode ter até 50 caracteres.')])
    status = SelectField('Status', choices=[
        ('Disponível', 'Disponível'), ('Debilitado', 'Debilitado'),
        ('Em Manutenção', 'Em Manutenção')])
    submit = SubmitField('Atualizar')

class TipoEquipamentoForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    submit = SubmitField('Cadastrar')

    def validate_nome(self, nome):
        nome = TipoEquipamento.query.filter_by(
            nome=nome.data).first()
        if nome:
            raise ValidationError('Já existe um tipo de equipamento com esse\
                nome. Por favor, insira um diferente.')