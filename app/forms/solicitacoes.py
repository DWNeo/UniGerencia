from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import (DataRequired, InputRequired, ValidationError, 
                                NumberRange, Length)
from wtforms.fields.html5 import IntegerField, TimeField, DateField

from app import fuso_horario
from app.locale import (obrigatorio, data_invalida, num_invalido_2, 
                        num_invalido_20, max_20, max_50)


class SolicitacaoEquipamentoForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message=obrigatorio)],
        coerce=int)
    tipo_equipamento = SelectField('Tipo de Equipamento', validators=[
        InputRequired()], coerce=int)
    qtd_preferencia = IntegerField('Quantidade', validators=[
        DataRequired(message=obrigatorio), 
        NumberRange(min=1, max=10, message=num_invalido_20)])
    descricao = StringField('Descrição', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=50, message=max_50)])
    data_inicio_pref = DateField('Data de Início Preferencial', 
        format='%Y-%m-%d', default=datetime.now().astimezone(fuso_horario).date())
    data_fim_pref = DateField('Data de Fim Preferencial', 
        format='%Y-%m-%d', default=datetime.now().astimezone(fuso_horario).date())
    submit = SubmitField('Solicitar')
    
    # Valida as datas de início e fim inseridas no formulário
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if self.data_inicio_pref.data < datetime.now().astimezone(fuso_horario).date():
            self.data_inicio_pref.errors.append('Esta data não pode ser antes de hoje.')
            return False
        elif self.data_fim_pref.data < self.data_inicio_pref.data:
            self.data_fim_pref.errors.append('Esta data não pode ser antes da de início.')
            return False
        
        return True
class SolicitacaoSalaForm(FlaskForm):

    turno = SelectField('Turno', validators=[
        DataRequired(message=obrigatorio)], coerce=int)
    setor = SelectField('Setor', validators=[
        DataRequired(message=obrigatorio)], coerce=int)
    qtd_preferencia = IntegerField('Quantidade', validators=[
        DataRequired(message=obrigatorio), 
        NumberRange(min=1, max=2, message=num_invalido_2)])
    descricao = StringField('Descrição', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=50, message=max_50)])
    data_inicio_pref = DateField('Data de Início Preferencial', 
        format='%Y-%m-%d', default=datetime.now().astimezone(fuso_horario).date())
    data_fim_pref = DateField('Data de Fim Preferencial', 
        format='%Y-%m-%d', default=datetime.now().astimezone(fuso_horario).date())
    submit = SubmitField('Solicitar')

    # Valida as datas de início e fim inseridas no formulário
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if self.data_inicio_pref.data < datetime.now().astimezone(fuso_horario).date():
            self.data_inicio_pref.errors.append('Esta data não pode ser antes de hoje.')
            return False
        elif self.data_fim_pref.data < self.data_inicio_pref.data:
            self.data_fim_pref.errors.append('Esta data não pode ser antes da de início.')
            return False
        else:
            return True


class ConfirmaSolicitacaoEquipamentoForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    tipo_equipamento = StringField('Tipo de Equipamento', 
        render_kw={'disabled':''})
    quantidade = IntegerField('Quantidade Solicitada', 
        render_kw={'disabled':''})
    qtd_disponivel = StringField('Quantidade Disponível', 
        render_kw={'disabled':''})
    equipamentos = SelectMultipleField('Equipamentos', 
        validators=[DataRequired(message=obrigatorio)], 
        render_kw={'multiple':'multiple'}, coerce=int)
    data_inicio_pref = StringField('Data de Início Preferencial', 
        render_kw={'disabled':''})
    data_fim_pref = StringField('Data de Fim Preferencial', 
        render_kw={'disabled':''})
    submit = SubmitField('Confirmar')


class ConfirmaSolicitacaoSalaForm(FlaskForm):

    autor = StringField('Autor', render_kw={'disabled':''})
    identificacao = StringField('Identificação', render_kw={'disabled':''})
    data_abertura = StringField('Data de Abertura', render_kw={'disabled':''})
    turno = StringField('Turno', render_kw={'disabled':''})
    setor = StringField('Setor', render_kw={'disabled':''})
    quantidade = IntegerField('Quantidade Solicitada', 
        render_kw={'disabled':''})
    qtd_disponivel = StringField('Quantidade Disponível', 
        render_kw={'disabled':''})
    salas = SelectMultipleField('Salas', 
        validators=[DataRequired(message=obrigatorio)], 
        render_kw={'multiple':'multiple'}, coerce=int)
    data_inicio_pref = StringField('Data de Início Preferencial', 
        render_kw={'disabled':''})
    data_fim_pref = StringField('Data de Fim Preferencial', 
        render_kw={'disabled':''})
    submit = SubmitField('Confirmar')


class EntregaSolicitacaoForm(FlaskForm):

    data_inicio_pref = StringField('Data de Início Preferencial', 
        render_kw={'disabled':''})
    data_fim_pref = StringField('Data de Fim Preferencial', 
        render_kw={'disabled':''})
    data_devolucao = DateField('Data de Devolução', 
        format='%Y-%m-%d', default=datetime.now().astimezone(fuso_horario).date())
    submit = SubmitField('Confirmar')

    def validate_data_devolucao(self, data_devolucao):
        if data_devolucao.data < datetime.now().astimezone(fuso_horario).date():
            raise ValidationError(data_invalida)


class TurnoForm(FlaskForm):
    nome = StringField('Nome',  validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)] )
    hora_inicio = TimeField('Data de Início', 
        format='%H:%M', default=datetime.now().astimezone(fuso_horario))
    hora_fim = TimeField('Data de Fim', 
        format='%H:%M', default=datetime.now().astimezone(fuso_horario))
    submit = SubmitField('Cadastrar')
    
     # Valida as datas de início e fim inseridas no formulário
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if self.hora_fim.data < self.hora_inicio.data:
            self.hora_inicio.errors.append('Hora de inicio não pode ser depois da de início.')
            self.hora_fim.errors.append('Hora de fim não pode ser antes da de início.')
            return False
        elif self.hora_fim.data == self.hora_inicio.data:
            self.hora_inicio.errors.append('As horas não podem ser iguais.')
            self.hora_fim.errors.append('As horas não podem ser iguais.')
            return False
        else:
            return True
    