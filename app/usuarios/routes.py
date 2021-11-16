from flask import render_template, url_for, flash, redirect, abort, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import Usuario, Post
from app.usuarios.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm, AdminAccountForm)
from app.usuarios.utils import save_picture, send_reset_email

usuarios = Blueprint('usuarios', __name__)


@usuarios.route("/registrar", methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Usuario(name=form.name.data, identification=form.identification.data,
                       username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi registrada com sucesso! Você já pode realizar o login.', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('usuarios/registrar.html', title='Registre-se', form=form)


@usuarios.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.active == False:
                flash('Este usuário está inativo e não pode ser utilizado.', 'danger')
                logout_user()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('principal.inicio'))
        else:
            flash('Erro ao realizar login. Por favor, verifique o email e senha inseridos.', 'danger')
    return render_template('usuarios/login.html', title='Login', form=form)


@usuarios.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('principal.inicio'))


@usuarios.route("/perfil", methods=['GET', 'POST'])
@login_required
def perfil():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.name = form.name.data
        current_user.identification = form.identification.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Sua conta foi atualizada com sucesso!', 'success')
        return redirect(url_for('usuarios.perfil'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.identification.data = current_user.identification
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img_perfil/' + current_user.image_file)
    return render_template('usuarios/perfil.html', title='Perfil',
                           image_file=image_file, form=form)


@usuarios.route("/usuarios/<string:username>")
@login_required
def posts_usuario(username):
    page = request.args.get('page', 1, type=int)
    usuario = Usuario.query.filter_by(username=username).first_or_404()
    if usuario.active == False:
        abort(404)
    posts = Post.query.filter_by(author=usuario)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('usuarios/posts_usuario.html', posts=posts, user=usuario)

@usuarios.route("/usuarios/<int:usuario_id>/atualizar", methods=['GET', 'POST'])
@login_required
def atualiza_usuario(usuario_id):
    if current_user.admin == False:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.active == False:
        abort(404)
    form = AdminAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            usuario.image_file = picture_file
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usuario.password = hashed_password
        usuario.name = form.name.data
        usuario.admin = form.admin.data
        db.session.commit()
        flash('A conta do usuário foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio'))
    elif request.method == 'GET':
        form.name.data = usuario.name
        form.admin.data = usuario.admin
    image_file = url_for('static', filename='img_perfil/' + usuario.image_file)
    return render_template('usuarios/atualizar_usuario.html', title='Atualizar Usuário',
                           image_file=image_file, form=form, legend='Atualizar Usuário')

@usuarios.route("/usuarios/<int:usuario_id>/excluir", methods=['POST'])
@login_required
def exclui_usuario(usuario_id):
    if current_user.admin == False:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.active == False:
        abort(404)
    if current_user.id == usuario.id:
        flash('Não é possível excluir a própria conta!', 'danger')
        return redirect(url_for('principal.inicio'))
    usuario.active = False
    db.session.commit()
    flash('O usuário foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))

@usuarios.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Um email foi enviado com instruções de como proceder com a redifinição da senha.', 'info')
        return redirect(url_for('usuarios.login'))
    return render_template('usuarios/redefinir_senha.html', title='Redefinição de Senha', form=form)


@usuarios.route("/redefinir_senha/<token>", methods=['GET', 'POST'])
def redefinir_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))
    user = Usuario.verify_reset_token(token)
    if user is None:
        flash('Este token é inválido ou já expirou.', 'warning')
        return redirect(url_for('usuarios.redefinir_senha'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Sua senha foi atualizada com sucesso! Você já pode realizar login usando ela.', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('usuarios/redefinir_token.html', title='Redefinir Senha', form=form)
