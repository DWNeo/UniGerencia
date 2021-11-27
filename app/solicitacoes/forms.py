from datetime import datetime, date

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired, ValidationError
from wtforms.fields.html5 import DateField

from app import fuso_horario
from app.locale import (obrigatorio, data_preferencial_invalida)

class SolicitacaoEquipamentoForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message=obrigatorio)],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    tipo_equipamento = SelectField('Tipo de Equipamento', validators=[
        InputRequired()], coerce=int)
    data_preferencial = DateField('Data Preferencial (Opcional)',
        default=datetime.now().astimezone(fuso_horario))
    submit = SubmitField('Solicitar')

    def validate_data_preferencial(self, data_preferencial):
        if data_preferencial.data < datetime.now().astimezone(fuso_horario).date():
            raise ValidationError('A data preferencial não pode ser antes\
                da data de hoje.')


class SolicitacaoSalaForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message=obrigatorio)],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    sala = SelectField('Sala', validators=[InputRequired()], coerce=int)
    data_preferencial = DateField('Data Preferencial (Opcional)',
        default=datetime.now().astimezone(fuso_horario))
    submit = SubmitField('Solicitar')

    def validate_data_preferencial(self, data_preferencial):
        if data_preferencial.data < datetime.now().astimezone(fuso_horario).date():
            raise ValidationError('A data preferencial não pode ser antes\
                da data de hoje.')


class ConfirmaSolicitacaoEquipamentoForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    tipo_equipamento = StringField('Tipo de Equipamento', 
        render_kw={'disabled':''})
    qtd_disponivel = StringField('Quantidade Disponível', 
        render_kw={'disabled':''})
    equipamento = SelectField('Equipamento', 
        validators=[InputRequired()], coerce=int)
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