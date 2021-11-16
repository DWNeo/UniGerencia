from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Equipamento


class EquipamentoForm(FlaskForm):
    patrimonio = StringField('Patrimônio', validators=[DataRequired(message='Este campo é obrigatório.'), Length(min=1, max=20, message='Este campo precisa ter entre 1 e 20 caracteres.')])
    descricao = StringField('Descrição', validators=[DataRequired(message='Este campo é obrigatório.'), Length(min=1, max=50, message='Este campo precisa ter menos de 50 caracteres.')])
    tipo_eqp = SelectField('Tipo', validators=[DataRequired(message='Este campo é obrigatório.')],
                            choices=[('Notebook', 'Notebook'), ('Tablet', 'Tablet'), ('Outro', 'Outro')])
    #status = SelectField('Status', choices=[('Disponível', 'Disponível'), ('Em Uso', 'Em Uso'), ('Debilitado', 'Debilitado'), ('Em Manutenção', 'Em Manutenção'), ('Indisponível', 'Indisponível')])
    submit = SubmitField('Cadastrar')

    def validate_patrimonio(self, patrimonio):
        equipamento = Equipamento.query.filter_by(patrimonio=patrimonio.data).first()
        if equipamento:
            raise ValidationError('Já existe um equipamento com esse patrimônio. Por favor, insira um diferente.')

class AtualizaEquipamentoForm(FlaskForm):
    #patrimonio = StringField('Patrimônio', validators=[DataRequired(message='Este campo é obrigatório.'), Length(min=1, max=20, message='Este campo precisa ter entre 1 e 20 caracteres.')])
    descricao = StringField('Descrição', validators=[DataRequired(message='Este campo é obrigatório.'), 
                            Length(min=1, max=50, message='Este campo precisa ter menos de 50 caracteres.')])
    tipo_eqp = SelectField('Tipo', choices=[('Notebook', 'Notebook'), ('Tablet', 'Tablet'), ('Outro', 'Outro')])
    status = SelectField('Status', choices=[('Disponível', 'Disponível'), ('Em Uso', 'Em Uso'), ('Debilitado', 'Debilitado'), ('Em Manutenção', 'Em Manutenção'), ('Indisponível', 'Indisponível')])
    submit = SubmitField('Atualizar')