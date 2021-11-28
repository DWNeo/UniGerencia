from datetime import datetime, date

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import (DataRequired, InputRequired, 
                                ValidationError, NumberRange)
from wtforms.fields.html5 import DateField, IntegerField, DateTimeLocalField

from app import fuso_horario
from app.locale import (obrigatorio, data_invalida, num_invalido)


class SolicitacaoEquipamentoForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message=obrigatorio)],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    tipo_equipamento = SelectField('Tipo de Equipamento', validators=[
        InputRequired()], coerce=int)
    qtd_equipamento = IntegerField('Quantidade', validators=[
        DataRequired(message=obrigatorio), 
        NumberRange(min=1, max=50, message=num_invalido)])
    data_preferencial = DateTimeLocalField('Data Preferencial', 
        format='%Y-%m-%dT%H:%M', default=datetime.now().astimezone(fuso_horario))
    submit = SubmitField('Solicitar')

    def validate_data_preferencial(self, data_preferencial):
        if data_preferencial.data < datetime.now():
            raise ValidationError(data_invalida)


class SolicitacaoSalaForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message=obrigatorio)],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    sala = SelectField('Sala', validators=[
        DataRequired(message=obrigatorio)], coerce=int)
    data_preferencial = DateTimeLocalField('Data Preferencial', 
        format='%Y-%m-%dT%H:%M', default=datetime.now().astimezone(fuso_horario))
    submit = SubmitField('Solicitar')

    def validate_data_preferencial(self, data_preferencial):
        if data_preferencial.data < datetime.now():
            raise ValidationError(data_invalida)


class ConfirmaSolicitacaoEquipamentoForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    tipo_equipamento = StringField('Tipo de Equipamento', 
        render_kw={'disabled':''})
    qtd_solicitada = IntegerField('Quantidade Solicitada', 
        render_kw={'disabled':''})
    qtd_disponivel = StringField('Quantidade Disponível', 
        render_kw={'disabled':''})
    equipamentos = SelectMultipleField('Equipamentos', 
        validators=[DataRequired(obrigatorio)], 
        render_kw={'multiple':'multiple'}, coerce=int)
    data_preferencial = DateField('Data Preferencial', 
        render_kw={'disabled':''})
    submit = SubmitField('Confirmar')


class ConfirmaSolicitacaoSalaForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    sala_solicitada = StringField('Sala Solicitada', render_kw={'disabled':''})
    data_preferencial = DateField('Data Preferencial', 
        render_kw={'disabled':''})
    submit = SubmitField('Confirmar')

class EntregaSolicitacaoForm(FlaskForm):

    data_devolucao = DateTimeLocalField('Data de Devolução', 
        format='%Y-%m-%dT%H:%M', default=datetime.now().astimezone(fuso_horario))
    submit = SubmitField('Confirmar')

    def validate_data_devolucao(self, data_devolucao):
        if data_devolucao.data < datetime.now():
            print('TESTE VALIDATE')
            raise ValidationError(data_invalida)