from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, InputRequired


class SolicitacaoEquipamentoForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message='Este campo é obrigatório.')],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    tipo_equipamento = SelectField('Tipo de Equipamento', coerce=int)
    submit = SubmitField('Solicitar')


class SolicitacaoSalaForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message='Este campo é obrigatório.')],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    sala = SelectField('Sala', coerce=int)
    submit = SubmitField('Solicitar')


class ConfirmaSolicitacaoEquipamentoForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    tipo_equipamento = StringField('Tipo de Equipamento', 
        render_kw={'disabled':''})
    qtd_disponivel = StringField('Quantidade Disponível', 
        render_kw={'disabled':''})
    equipamento = SelectField('Equipamento', coerce=int)
    submit = SubmitField('Confirmar')


class ConfirmaSolicitacaoSalaForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    sala = StringField('Sala', render_kw={'disabled':''})
    submit = SubmitField('Confirmar')