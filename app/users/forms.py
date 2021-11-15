from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User


class RegistrationForm(FlaskForm):
    class Meta:
        locales = ['pt_BR', 'pt']
    username = StringField('Usuário',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=2, max=20, message='Este campo precisa ter entre 2 e 20 caracteres.')])
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    password = PasswordField('Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(message='Este campo é obrigatório.'), 
                                     EqualTo('password', message='Os dois campos não são identicos.')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este usuário já está sendo utilizado. Por favor, escolha um diferente.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está sendo utilizado. Por favor, escolha um diferente.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    password = PasswordField('Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    remember = BooleanField('Lembrar')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Usuário',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=2, max=20, message='Este campo precisa ter entre 2 e 20 caracteres.')])
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    picture = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'], message='Formato de imagem inválido.')])
    submit = SubmitField('Atualizar')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este usuário já está sendo utilizado. Por favor, escolha um diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email já está sendo utilizado. Por favor, escolha um diferente.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    submit = SubmitField('Redefinir Senha')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Não existe uma conta com esse email. Por favor, cadastre uma conta primeiro.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(message='Este campo é obrigatório.'), 
                                     EqualTo('password', message='Os dois campos não são identicos.')])
    submit = SubmitField('Redefinir Senha')
