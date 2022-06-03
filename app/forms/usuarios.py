from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from app.models import Usuario
from app.locale import (obrigatorio, max_20, max_100, identificacao_existente,
                        email_invalido, email_existente, email_inexistente,
                        imagem_invalida, senha_diferente)

# Formulário para cadastro normal de um novo usuário
class RegistraForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=100, message=max_100)])
    identificacao = StringField('Identificação (RA/CPF)', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)])
    email = StringField('Email', validators=[
        DataRequired(message=obrigatorio), 
        Email(message=email_invalido)])
    senha = PasswordField('Senha', validators=[
        DataRequired(message=obrigatorio)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message=obrigatorio), 
        EqualTo('senha', message=senha_diferente)])
    tipo = SelectField(u'Tipo Usuário', choices=[('ALUNO', 'Aluno'), ('PROF','Professor')])
    submit = SubmitField('Registrar')

    # Valida se a identificação inserida no formulário é única
    def validate_identificacao(self, identificacao):
        usuario = Usuario.query.filter_by(
            identificacao=identificacao.data).first()
        if usuario:
            raise ValidationError(identificacao_existente)

    # Valida se o email inserido no formulário é único
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError(email_existente)

# Formulário para login do usuário
class LoginForm(FlaskForm):

    email = StringField('Email', validators=[
        DataRequired(message=obrigatorio), 
        Email(message=email_invalido)])
    senha = PasswordField('Senha', validators=[
        DataRequired(message=obrigatorio)])
    lembrar = BooleanField('Lembrar')
    submit = SubmitField('Login')

# Formulário para atualização dentro do perfil do usuário
class AtualizaPerfilForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=100, message=max_100)])
    identificacao = StringField('Identificação (RA/CPF)', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)])
    email = StringField('Email', validators=[
        DataRequired(message=obrigatorio), 
        Email(message=email_invalido)])
    senha = PasswordField('Senha', validators=[
        DataRequired(message=obrigatorio)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message=obrigatorio), 
        EqualTo('senha', message=senha_diferente)])
    imagem = FileField('Imagem de Perfil', validators=[
        FileAllowed(['jpg', 'png'], message=imagem_invalida)])
    tipo = SelectField(u'Tipo Usuário', choices=[('ALUNO', 'Aluno'), ('PROF','Professor'), ('ADMIN', 'Administrador')])
    submit = SubmitField('Atualizar')

    def validate_identificacao(self, identificacao):
        if identificacao.data != current_user.identificacao:
            usuario = Usuario.query.filter_by(
                identificacao=identificacao.data).first()
            if usuario:
                raise ValidationError(identificacao_existente)

    def validate_email(self, email):
        if email.data != current_user.email:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError(email_existente)

# Formulário para atualização de um usuário por um admin
class AdminAtualizaPerfilForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=100, message=max_100)])
    senha = PasswordField('Senha', validators=[
        DataRequired(message=obrigatorio)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message=obrigatorio), 
        EqualTo('senha', message=senha_diferente)])
    imagem = FileField('Imagem de Perfil', validators=[
        FileAllowed(['jpg', 'png'], message=imagem_invalida)])
    tipo = SelectField(u'Tipo Usuário', choices=[('ALUNO', 'Aluno'), ('PROF','Professor'), ('ADMIN', 'Administrador')])
    submit = SubmitField('Atualizar')

# Formulário para cadastro de um novo usuário por um admin
class AdminRegistraForm(FlaskForm):

    nome = StringField('Nome', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=100, message=max_100)])
    identificacao = StringField('Identificação (RA/CPF)', validators=[
        DataRequired(message=obrigatorio), 
        Length(max=20, message=max_20)])
    email = StringField('Email', validators=[
        DataRequired(message=obrigatorio), 
        Email(message=email_invalido)])
    senha = PasswordField('Senha', validators=[
        DataRequired(message=obrigatorio)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message=obrigatorio), 
        EqualTo('senha', message=senha_diferente)])
    imagem = FileField('Imagem de Perfil', validators=[
        FileAllowed(['jpg', 'png'], message=imagem_invalida)])
    tipo = SelectField(u'Tipo Usuário', choices=[('ALUNO', 'Aluno'), ('PROF','Professor'), ('ADMIN', 'Administrador')])
    submit = SubmitField('Registrar')

    def validate_identificacao(self, identificacao):
        usuario = Usuario.query.filter_by(
            identificacao=identificacao.data).first()
        if usuario:
            raise ValidationError(identificacao_existente)

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError(email_existente)

# Formulário para realizar um pedido de redefinição de senha
class RedefineSenhaForm(FlaskForm):

    email = StringField('Email', validators=[
        DataRequired(message=obrigatorio), 
        Email(message=email_invalido)])
    submit = SubmitField('Redefinir Senha')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario is None:
            raise ValidationError(email_inexistente)

# Formulário para redefinir a senha após a verificação do token
class NovaSenhaForm(FlaskForm):

    senha = PasswordField('Nova Senha', validators=[
        DataRequired(message=obrigatorio)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message=obrigatorio), 
        EqualTo('senha', message=senha_diferente)])
    submit = SubmitField('Redefinir Senha')
    