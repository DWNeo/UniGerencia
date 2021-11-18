from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from app.models import Usuario


class RegistraForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=100, message='Este campo só pode ter até 100 caracteres.')])
    identificacao = StringField('Identificação (RA/CPF)', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    email = StringField('Email', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Email(message='Este email é inválido.')])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        EqualTo('senha', message='Os dois campos não são identicos.')])
    submit = SubmitField('Registrar')

    def validate_identificacao(self, identificacao):
        usuario = Usuario.query.filter_by(
            identificacao=identificacao.data).first()
        if usuario:
            raise ValidationError('Esta identificação já está sendo utilizada.\
                Por favor, escolha uma diferente.')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está sendo utilizado.\
                Por favor, escolha um diferente.')


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Email(message='Este email é inválido.')])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    lembrar = BooleanField('Lembrar')
    submit = SubmitField('Login')


class AtualizaPerfilForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=100, message='Este campo só pode ter até 100 caracteres.')])
    identificacao = StringField('Identificação (RA/CPF)', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    email = StringField('Email', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Email(message='Este email é inválido.')])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        EqualTo('senha', message='Os dois campos não são identicos.')])
    imagem = FileField('Imagem de Perfil', validators=[
        FileAllowed(['jpg', 'png'], message='Formato de imagem inválido.')])
    submit = SubmitField('Atualizar')

    def validate_identificacao(self, identificacao):
        if identificacao.data != current_user.identificacao:
            usuario = Usuario.query.filter_by(
                identificacao=identificacao.data).first()
            if usuario:
                raise ValidationError('Esta identificação já está\
                    sendo utilizada. Por favor, escolha uma diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Este email já está sendo utilizado.\
                    Por favor, escolha um diferente.')


class AdminAtualizaPerfilForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=100, message='Este campo só pode ter até 100 caracteres.')])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        EqualTo('senha', message='Os dois campos não são identicos.')])
    imagem = FileField('Imagem de Perfil', validators=[
        FileAllowed(['jpg', 'png'], message='Formato de imagem inválido.')])
    admin = BooleanField('Administrador')
    submit = SubmitField('Atualizar')


class AdminRegistraForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=100, message='Este campo só pode ter até 100 caracteres.')])
    identificacao = StringField('Identificação (RA/CPF)', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Length(max=20, message='Este campo só pode ter até 20 caracteres.')])
    email = StringField('Email', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Email(message='Este email é inválido.')])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        EqualTo('senha', message='Os dois campos não são identicos.')])
    imagem = FileField('Imagem de Perfil', validators=[
        FileAllowed(['jpg', 'png'], message='Formato de imagem inválido.')])
    admin = BooleanField('Administrador')
    submit = SubmitField('Registrar')

    def validate_identificacao(self, identificacao):
        usuario = Usuario.query.filter_by(
            identificacao=identificacao.data).first()
        if usuario:
            raise ValidationError('Esta identificação já está sendo utilizada.\
                Por favor, escolha uma diferente.')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está sendo utilizado.\
                Por favor, escolha um diferente.')


class RedefineSenhaForm(FlaskForm):

    email = StringField('Email', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        Email(message='Este email é inválido.')])
    submit = SubmitField('Redefinir Senha')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario is None:
            raise ValidationError('Não existe uma conta com esse email.\
                Por favor, cadastre uma conta primeiro.')


class NovaSenhaForm(FlaskForm):

    senha = PasswordField('Nova Senha', validators=[
        DataRequired(message='Este campo é obrigatório.')])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Este campo é obrigatório.'), 
        EqualTo('senha', message='Os dois campos não são identicos.')])
    submit = SubmitField('Redefinir Senha')