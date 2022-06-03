from datetime import datetime

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, logout_user, login_required

from app.models import Post, Solicitacao, Usuario
from app.forms.usuarios import (RegistraForm, LoginForm, AtualizaPerfilForm, 
                                RedefineSenhaForm, NovaSenhaForm,
                                AdminRegistraForm, AdminAtualizaPerfilForm)
                                 
from app.utils import (envia_email_redefinicao, admin_required)

usuarios = Blueprint('usuarios', __name__)


@usuarios.route("/<int:usuario_id>", methods=['GET'])
@login_required
@admin_required
def usuario(usuario_id):
    # Recupera a sala pela ID
    usuario = Usuario.recupera_id(usuario_id)

    # Recupera as 5 últimas solicitações associadas ao usuário
    solicitacoes = Solicitacao.recupera_autor_limite(usuario, 5)

    # Renderiza o template
    return render_template('usuarios/usuario.html', 
                           title=usuario, usuario=usuario,
                           solicitacoes=solicitacoes)


@usuarios.route("/registrar", methods=['GET', 'POST'])
def registrar():
    # Retorna o usuário à página principal caso ele já esteja autenticado
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))

    # Valida os dados do formulário enviado e insere um 
    # novo registro de usuário no banco de dados
    form = RegistraForm()
    if form.validate_on_submit():
        usuario = Usuario.cria(form)
        Usuario.insere(usuario)
        flash('Sua conta foi registrada com sucesso!\
              Você já pode realizar o login.', 'success')
        return redirect(url_for('usuarios.login'))
    
    # Renderiza o template
    return render_template('usuarios/registrar.html', 
                           title='Registre-se', form=form)


@usuarios.route("/login", methods=['GET', 'POST'])
def login():
    # Retorna o usuário à página principal caso ele já esteja autenticado
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))

     # Valida os dados do formulário
    form = LoginForm()
    if form.validate_on_submit():
        # Recupera o usuário de acordo com o email inserido no formulário
        usuario = Usuario.recupera_email(form.email.data)

        # Verifica se o email e o hash da senha inserida estão ambos
        # corretos e só então realiza o login do usuário
        if Usuario.login(usuario, form):
            # Após o login, redireciona o usuário para a última página acessada
            prox_pagina = request.args.get('next')
            if (prox_pagina):
                return redirect(prox_pagina) 
            else:
                redirect(url_for('principal.inicio'))
        else:
            flash('Erro ao realizar login. Por favor, verifique\
                  o email e senha inseridos.', 'danger')

    return render_template('usuarios/login.html', title='Login', form=form)


@usuarios.route("/logout", methods=['GET'])
def logout():
    # Realiza o logout do usuário que está atualmente autenticado
    logout_user()
    return redirect(url_for('principal.inicio'))


@usuarios.route("/perfil", methods=['GET', 'POST'])
@login_required
def perfil():
    # Valida os dados do formulário enviado e atualiza
    # o registro do usuário atual no banco de dados
    form = AtualizaPerfilForm()
    if form.validate_on_submit():
        Usuario.atualiza(current_user, form)
        flash('Sua conta foi atualizada com sucesso!', 'success')
        return redirect(url_for('usuarios.perfil'))  
    elif request.method == 'GET':
        form.nome.data = current_user.nome
        form.identificacao.data = current_user.identificacao
        form.email.data = current_user.email

    # Obtem o link para o caminho completo da imagem de perfil do usuário
    imagem_perfil = url_for('static', filename='img_perfil/' 
                             + current_user.imagem_perfil)

    return render_template('usuarios/perfil.html', title='Perfil',
                           imagem_perfil=imagem_perfil, form=form)


@usuarios.route("/<int:usuario_id>/posts", methods=['GET'])
@login_required
@admin_required
def posts_usuario(usuario_id):
    # Recebe o argumento que define qual os posts que serão
    # recuperados e exibidos na página
    pagina = request.args.get('pagina', 1, type=int)

    # Recupera e realiza a paginação dos posts de que o usuário é autor
    # Os posts recuperados depende do argumento acima
    usuario = Usuario.recupera_id(usuario_id)
    posts = Post.recupera_autor_paginado(usuario, pagina, 5)

    return render_template('usuarios/posts_usuario.html', 
                           posts=posts, usuario=usuario)

@usuarios.route("/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    form = AdminRegistraForm()
    if form.validate_on_submit():
        Usuario.insere(form)
        flash('A conta foi registrada com sucesso!.', 'success')
        return redirect(url_for('principal.inicio', tab=5))

    return render_template('usuarios/novo_usuario.html', 
                           title='Novo Usuário', form=form)

@usuarios.route("/<int:usuario_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_usuario(usuario_id):
    usuario = Usuario.recupera_id(usuario_id)
    # Valida os dados do formulário enviado e atualiza
    # o registro do usuário especificado no banco de dados
    form = AdminAtualizaPerfilForm()
    if form.validate_on_submit():
        Usuario.atualiza(usuario, form)
        flash('A conta do usuário foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=5))
    elif request.method == 'GET':
        form.nome.data = usuario.nome
        form.tipo.data = usuario.tipo.name
    imagem_perfil = url_for('static', filename='img_perfil/' 
                         + usuario.imagem_perfil)

    return render_template('usuarios/atualizar_usuario.html', 
                           title='Atualizar Usuário', form=form,
                           imagem_perfil=imagem_perfil, 
                           legend='Atualizar Usuário')

@usuarios.route("/<int:usuario_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_usuario(usuario_id):
    usuario = Usuario.recupera_id(usuario_id)

    # Impede o usuário de excluir a própria conta
    if current_user.id == usuario.id:
        flash('Não é possível excluir a própria conta!', 'danger')
        return redirect(url_for('principal.inicio', tab=5))

    # Desativa o registro do usuário especificado
    Usuario.exclui(usuario)
    flash('O usuário foi excluído com sucesso!', 'success')
    
    return redirect(url_for('principal.inicio', tab=5))

@usuarios.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    # Retorna o usuário à página principal caso ele já esteja autenticado
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))

    form = RedefineSenhaForm()
    if form.validate_on_submit():
        usuario = Usuario.recupera_email(form.email.data)
        # Envia uma mensagem de refinição de senha para o 
        # email do usuário utilizando uma função auxilar
        envia_email_redefinicao(usuario)
        flash('Um email foi enviado com instruções de como\
              proceder com a redefinição da senha.', 'info')
        return redirect(url_for('usuarios.login'))

    return render_template('usuarios/redefinir_senha.html', 
                           title='Redefinição de Senha', form=form)


@usuarios.route("/redefinir_senha/<token>", methods=['GET', 'POST'])
def redefinir_token(token):
    # Retorna o usuário à página principal caso ele já esteja autenticado
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))

    # Verifica se o token inserido pelo usuário é válido
    # A verificação é realiza com base no token gerado pela
    # função 'obtem_token_redefinicao' da classe Usuario
    usuario = Usuario.verifica_token_redefinicao(token)
    if usuario is None:
        flash('Este token é inválido ou já expirou.', 'warning')
        return redirect(url_for('usuarios.redefinir_senha'))

    form = NovaSenhaForm()
    if form.validate_on_submit():
        Usuario.nova_senha(usuario, form.senha.data)
        flash('Sua senha foi atualizada com sucesso!\
              Você já pode realizar login usando ela.', 'success')
        return redirect(url_for('usuarios.login'))

    return render_template('usuarios/redefinir_token.html', 
                           title='Redefinir Senha', form=form)
