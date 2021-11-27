from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import login_user, current_user, logout_user, login_required

from app import db, bcrypt
from app.models import Usuario, Post
from app.usuarios.forms import (RegistraForm, LoginForm, AtualizaPerfilForm, 
                                RedefineSenhaForm, NovaSenhaForm,
                                AdminRegistraForm, AdminAtualizaPerfilForm)
                                 
from app.usuarios.utils import (salva_imagem, envia_email_redefinicao, 
                                admin_required)

usuarios = Blueprint('usuarios', __name__)


@usuarios.route("/registrar", methods=['GET', 'POST'])
def registrar():
    # Retorna o usuário à página principal caso ele já esteja autenticado
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))

    # Valida os dados do formulário enviado e insere um 
    # novo registro de usuário no banco de dados
    form = RegistraForm()
    if form.validate_on_submit():
        # Gera um hash da senha inserida pelo usuário para
        # ser armazenada no seu registro no banco de dados
        hash_senha = bcrypt.generate_password_hash(
            form.senha.data).decode('utf-8')
        usuario = Usuario(nome=form.nome.data, 
                          identificacao=form.identificacao.data,
                          email=form.email.data, 
                          senha=hash_senha)
        db.session.add(usuario)
        db.session.commit()
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
        usuario = Usuario.query.filter_by(
            email=form.email.data).filter_by(ativo=True).first()

        # Verifica se o email e o hash da senha inserida estão ambos
        # corretos e só então realiza o login do usuário
        if usuario and bcrypt.check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario, remember=form.lembrar.data)
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


@usuarios.route("/logout")
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
        # Realiza o tratamento da imagem enviada pelo  
        # usuário utilizando uma função auxiliar
        if form.imagem.data:
            arquivo_imagem = salva_imagem(form.imagem.data)
            current_user.imagem_perfil = arquivo_imagem
        # Gera o hash da senha atualizada
        hash_senha = bcrypt.generate_password_hash(
            form.senha.data).decode('utf-8')
        current_user.senha = hash_senha
        current_user.nome = form.nome.data
        current_user.identificacao = form.identificacao.data
        current_user.email = form.email.data
        db.session.commit()
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


@usuarios.route("/<int:usuario_id>/posts")
@login_required
def posts_usuario(usuario_id):
    # Recebe o argumento que define qual os posts que serão
    # recuperados e exibidos na página
    pagina = request.args.get('pagina', 1, type=int)

    # Recupera e realiza a paginação dos posts de que o usuário é autor
    # Os posts recuperados depende do argumento acima
    usuario = Usuario.query.filter_by(
        id=usuario_id).filter_by(ativo=True).first_or_404()
    posts = Post.query.filter_by(autor=usuario).order_by(
        Post.data_postado.desc()).paginate(page=pagina, per_page=5)

    return render_template('usuarios/posts_usuario.html', 
                           posts=posts, usuario=usuario)

@usuarios.route("/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    # Valida os dados do formulário
    form = AdminRegistraForm()
    if form.validate_on_submit():
        # Define o arquivo de imagem padrão
        arquivo_imagem = 'default.jpg'
        # Realiza o tratamento da imagem enviada
        if form.imagem.data:
            arquivo_imagem = salva_imagem(form.imagem.data)
            imagem_perfil = arquivo_imagem
        # Gera o hash da senha do novo usuário
        hash_senha = bcrypt.generate_password_hash(
            form.senha.data).decode('utf-8')
        usuario = Usuario(nome=form.nome.data, 
                          identificacao=form.identificacao.data,
                          email=form.email.data, 
                          senha=hash_senha,
                          imagem_perfil=imagem_perfil, 
                          admin=form.admin.data)
        db.session.add(usuario)
        db.session.commit()
        flash('A conta foi registrada com sucesso!.', 'success')
        return redirect(url_for('principal.inicio', tab=5))

    return render_template('usuarios/novo_usuario.html', 
                           title='Novo Usuário', form=form)

@usuarios.route("/<int:usuario_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_usuario(usuario_id):
    # Recupera o usuário pela ID e retorna erro 404 caso não encontre
    usuario = Usuario.query.filter_by(
            id=usuario_id).filter_by(ativo=True).first_or_404()

    # Valida os dados do formulário enviado e atualiza
    # o registro do usuário especificado no banco de dados
    form = AdminAtualizaPerfilForm()
    if form.validate_on_submit():
        # Realiza o tratamento da imagem enviada
        if form.imagem.data:
            arquivo_imagem = salva_imagem(form.imagem.data)
            usuario.imagem_perfil = arquivo_imagem
        # Gera o hash da senha do novo usuário    
        hash_senha = bcrypt.generate_password_hash(
            form.senha.data).decode('utf-8')
        usuario.senha = hash_senha
        usuario.nome = form.nome.data
        usuario.admin = form.admin.data
        db.session.commit()
        flash('A conta do usuário foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=5))
    elif request.method == 'GET':
        form.nome.data = usuario.nome
        form.admin.data = usuario.admin
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
    # Recupera o usuário pela ID e retorna erro 404 caso não encontre
    usuario = Usuario.query.filter_by(
            id=usuario_id).filter_by(ativo=True).first_or_404()

    # Impede o usuário de excluir a própria conta
    if current_user.id == usuario.id:
        flash('Não é possível excluir a própria conta!', 'danger')
        return redirect(url_for('principal.inicio', tab=5))

    # Desativa o registro do usuário especificado
    usuario.ativo = False
    db.session.commit()
    flash('O usuário foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=5))

@usuarios.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    # Retorna o usuário à página principal caso ele já esteja autenticado
    if current_user.is_authenticated:
        return redirect(url_for('principal.inicio'))

    form = RedefineSenhaForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        # Envia uma mensagem de refinição de senha para o 
        # email do usuário utilizando uma função auxilar
        envia_email_redefinicao(usuario)
        flash('Um email foi enviado com instruções de como\
              proceder com a redifinição da senha.', 'info')
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
        # Gera um novo hash com base na nova senha do usuário
        hash_senha = bcrypt.generate_password_hash(
            form.senha.data).decode('utf-8')
        usuario.senha = hash_senha
        db.session.commit()
        flash('Sua senha foi atualizada com sucesso!\
              Você já pode realizar login usando ela.', 'success')
        return redirect(url_for('usuarios.login'))

    return render_template('usuarios/redefinir_token.html', 
                           title='Redefinir Senha', form=form)
