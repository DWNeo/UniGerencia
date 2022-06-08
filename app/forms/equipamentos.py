from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField, 
                     TextAreaField, BooleanField)
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Equipamento, TipoEquipamento
from app.locale import (obrigatorio, max_20, max_50, 
                        patrimonio_existente, eqp_nome_existente)

# Formulário para cadastro de um novo equipamento
class EquipamentoForm(FlaskForm):

    patrimonio = StringField('Patrimônio', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)])
    descricao = StringField('Descrição', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=50, message=max_50)])
    tipo_eqp = SelectField('Tipo', coerce=int)
    submit = SubmitField('Cadastrar')

    def validate_patrimonio(self, patrimonio):
        equipamento = Equipamento.recupera_primeiro_patrimonio(patrimonio)
        if equipamento:
            raise ValidationError(patrimonio_existente)

# Formulário para atualização de um equipamento
class AtualizaEquipamentoForm(FlaskForm):

    descricao = StringField('Descrição', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=50, message=max_50)])
    submit = SubmitField('Atualizar')

# Formulário para cadastro de um novo tipo de quipamento
class TipoEquipamentoForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)])
    submit = SubmitField('Cadastrar')

    def validate_nome(self, nome):
        nome = TipoEquipamento.recupera_primeiro_nome(nome)
        if nome:
            raise ValidationError(eqp_nome_existente)

# Formulário para indisponibilização um equipamento
class IndisponibilizaEquipamentoForm(FlaskForm):
    
    motivo = TextAreaField('Motivo', validators=[
        DataRequired(message=obrigatorio)])
    submit = SubmitField('Confirmar')

# Formulário para cadastro de um novo relatório do equipamento
class RelatorioEquipamentoForm(FlaskForm):

    tipo = SelectField('Tipo do Relatório', choices=[
        ('REVISAO', 'Revisão'), ('MANUTENCAO', 'Manutenção'), ('OUTRO', 'Outro')])
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message=obrigatorio)])
    manutencao = BooleanField('Necessita de Manutenção?')
    defeito = BooleanField('Com Defeito?')
    detalhes = TextAreaField('Detalhes Adicionais')
    finalizar = BooleanField('Finalizar')
    submit = SubmitField('Cadastrar')

# Formulário para atualização de um relatório do equipamento
class AtualizaRelatorioEquipamentoForm(FlaskForm):

    tipo = StringField('Autor', render_kw={'disabled':''})
    conteudo = TextAreaField('Conteúdo', validators=[
        DataRequired(message=obrigatorio)])
    manutencao = BooleanField('Necessita de Manutenção?', render_kw={'disabled':''})
    defeito = BooleanField('Com Defeito?', render_kw={'disabled':''})
    detalhes = TextAreaField('Detalhes Adicionais')
    finalizar = BooleanField('Finalizar')
    submit = SubmitField('Atualizar')
    