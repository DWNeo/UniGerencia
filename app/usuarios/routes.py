from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import Usuario, Post
from app.usuarios.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from app.usuarios.utils import save_picture, send_reset_email

usuarios = Blueprint('usuarios', __name__)


@usuarios.route("/registrar", methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usuario = Usuario(usuario=form.usuario.data, email=form.email.data, 
                          senha=hashed_password), 
        db.session.add(usuario)
        db.session.commit()
        flash('Sua conta foi registrada com sucesso! Você já pode realizar o login.', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('registrar.html', title='Registre-se', form=form)


@usuarios.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Erro ao realizar login. Por favor, verifique o email e senha inseridos.', 'danger')
    return render_template('login.html', title='Login', form=form)


@usuarios.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@usuarios.route("/perfil", methods=['GET', 'POST'])
@login_required
def perfil():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Sua conta foi atualizada com sucesso!', 'success')
        return redirect(url_for('usuarios.perfil'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img_perfil/' + current_user.image_file)
    return render_template('perfil.html', title='Perfil',
                           image_file=image_file, form=form)


@usuarios.route("/usuario/<string:username>")
@login_required
def usuario(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('usuario.html', posts=posts, user=user)


@usuarios.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        send_reset_email(usuario)
        flash('Um email foi enviado com instruções de como proceder com a redifinição da senha.', 'info')
        return redirect(url_for('usuarios.login'))
    return render_template('redefinir_senha.html', title='Redefinição de Senha', form=form)


@usuarios.route("/redefinir_senha/<token>", methods=['GET', 'POST'])
def redefinir_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    usuario = Usuario.verificar_token_redefinicao(token)
    if usuario is None:
        flash('Este token é inválido ou já expirou.', 'warning')
        return redirect(url_for('usuarios.redefinir_senha'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usuario.senha = hashed_password
        db.session.commit()
        flash('Sua senha foi atualizada com sucesso! Você já pode realizar login usando ela.', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('redefinir_token.html', title='Redefinir Senha', form=form)
