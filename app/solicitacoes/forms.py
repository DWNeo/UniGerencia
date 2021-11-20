from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, InputRequired


class SolicitacaoEquipamentoForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message='Este campo é obrigatório.')],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    tipo_equipamento = SelectField('Tipo de Equipamento',
        choices=[('Notebook', 'Notebook'), ('Tablet', 'Tablet')])
    submit = SubmitField('Solicitar')


class AtualizaSolicitacaoEquipamentoForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    tipo_equipamento = StringField('Tipo de Equipamento', 
        render_kw={'disabled':''})
    equipamento = SelectField('Equipamentos Disponíveis')
    confirmar = BooleanField('Confirmar Solicitação')
    submit = SubmitField('Atualizar')


class SolicitacaoSalaForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message='Este campo é obrigatório.')],
        choices=[('Integral', 'Integral'), ('Matutino', 'Matutino'),\
                 ('Noturno', 'Noturno')])
    sala = SelectField('Salas Disponíveis', validators=[
        InputRequired(message='Escolha inválida.')])
    submit = SubmitField('Solicitar')


class AtualizaSolicitacaoSalaForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    sala = StringField('Sala Solicitada', render_kw={'disabled':''})
    submit = SubmitField('Confirmar')