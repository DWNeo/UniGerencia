from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import Usuario


class RegistrationForm(FlaskForm):
    name = StringField('Nome',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=100, message='Este campo precisa ter entre 3 e 100 caracteres.')])
    identification = StringField('Identificação (RA/CPF)',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=20, message='Este campo precisa ter entre 3 e 20 caracteres.')])
    username = StringField('Usuário',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=20, message='Este campo precisa ter entre 3 e 20 caracteres.')])
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    password = PasswordField('Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(message='Este campo é obrigatório.'), 
                                     EqualTo('password', message='Os dois campos não são identicos.')])
    submit = SubmitField('Registrar')

    def validate_identification(self, identification):
        user = Usuario.query.filter_by(identification=identification.data).first()
        if user:
            raise ValidationError('Esta identificação já está sendo utilizada. Por favor, escolha uma diferente.')

    def validate_username(self, username):
        user = Usuario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este usuário já está sendo utilizado. Por favor, escolha um diferente.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
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
    name = StringField('Nome',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=100, message='Este campo precisa ter entre 3 e 100 caracteres.')])
    identification = StringField('Identificação (RA/CPF)',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=20, message='Este campo precisa ter entre 3 e 20 caracteres.')])
    username = StringField('Usuário',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=20, message='Este campo precisa ter entre 3 e 20 caracteres.')])
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    password = PasswordField('Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(message='Este campo é obrigatório.'), 
                                     EqualTo('password', message='Os dois campos não são identicos.')])
    picture = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'], message='Formato de imagem inválido.')])
    submit = SubmitField('Atualizar')

    def validate_identification(self, identification):
        if identification.data != current_user.identification:
            user = Usuario.query.filter_by(identification=identification.data).first()
            if user:
                raise ValidationError('Esta identificação já está sendo utilizada. Por favor, escolha uma diferente.')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Usuario.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este usuário já está sendo utilizado. Por favor, escolha um diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Usuario.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email já está sendo utilizado. Por favor, escolha um diferente.')

class AdminAccountForm(FlaskForm):
    name = StringField('Nome',
                           validators=[DataRequired(message='Este campo é obrigatório.'), 
                           Length(min=3, max=100, message='Este campo precisa ter entre 3 e 100 caracteres.')])
    password = PasswordField('Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(message='Este campo é obrigatório.'), 
                                     EqualTo('password', message='Os dois campos não são identicos.')])
    picture = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'], message='Formato de imagem inválido.')])
    admin = BooleanField('Administrador')
    submit = SubmitField('Atualizar')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(message='Este campo é obrigatório.'), 
                        Email(message='Este email é inválido.')])
    submit = SubmitField('Redefinir Senha')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Não existe uma conta com esse email. Por favor, cadastre uma conta primeiro.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(message='Este campo é obrigatório.')])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(message='Este campo é obrigatório.'), 
                                     EqualTo('password', message='Os dois campos não são identicos.')])
    submit = SubmitField('Redefinir Senha')
