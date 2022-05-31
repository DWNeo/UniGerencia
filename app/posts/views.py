from datetime import datetime

from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required

from app import db, fuso_horario
from app.models import Post, Usuario
from app.posts.forms import PostForm, PostAdminForm, AtualizaPostForm

posts = Blueprint('posts', __name__)


@posts.route("/<int:post_id>")
@login_required
def post(post_id):
    # Recupera o post pela ID
    post = Post.query.filter_by(
        id=post_id).filter_by(ativo=True).first_or_404()

    # Permite acesso somente ao autor do post ou a um admin
    if post.autor != current_user and current_user.tipo.name != 'ADMIN':
        abort(403)

    # Renderiza o template
    return render_template('posts/post.html', title=post.titulo, post=post)


@posts.route("/novo", methods=['GET', 'POST'])
@login_required
def novo_post():
    # Preenche a lista de seleção de destinatário
    # Administradores podem escolher também o destinatário
    if current_user.tipo.name == 'ADMIN':
        form = PostAdminForm()
        usuarios = Usuario.query.filter_by(ativo=True).all()
        lista_usuarios=[(usuario.id, usuario) for usuario in usuarios]
        form.destinatario.choices = lista_usuarios
    else:  
        form = PostForm()
        form.destinatario.data = 'Administradores'
    
    if form.validate_on_submit():
        if current_user.tipo.name == 'ADMIN':
            usuario_id = form.destinatario.data
            usuario = Usuario.query.filter_by(
            id=usuario_id).filter_by(ativo=True).first_or_404()
        
            post = Post(titulo=form.titulo.data, 
                        destinatario=usuario,
                        conteudo=form.conteudo.data,
                        autor=current_user)
        else:
            post = Post(titulo=form.titulo.data, 
                        conteudo=form.conteudo.data,
                        autor=current_user)    
        db.session.add(post)
        db.session.commit()
        flash('Sua mensagem foi postada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=2))

    return render_template('posts/novo_post.html', title='Nova Mensagem',
                           form=form, legend='Nova Mensagem')


@posts.route("/<int:post_id>/atualizar", methods=['GET', 'POST'])
@login_required
def atualiza_post(post_id):
    # Recupera o post pela ID e retorna erro 404 caso não encontre
    post = Post.query.filter_by(
        id=post_id).filter_by(ativo=True).first_or_404()
    print(post.destinatario)

    # Impede o acesso a página de todos os usuários que 
    # não sejam o autor do post ou um admin
    if post.autor != current_user and current_user.tipo.name != 'ADMIN':
        abort(403)
        
    # Valida o formulário enviado e atualiza o registro
    # do post no banco de dados de acordo com ele
    form = AtualizaPostForm()
    if form.validate_on_submit():
        post.titulo = form.titulo.data
        post.conteudo = form.conteudo.data
        post.data_atualizacao = datetime.now().astimezone(fuso_horario)
        
        db.session.commit()
        flash('Sua mensagem foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=2))
    elif request.method == 'GET':
        if post.destinatario == None:
            form.destinatario.data = 'Administradores'
        else:
            form.destinatario.data = post.destinatario
        form.titulo.data = post.titulo
        form.conteudo.data = post.conteudo

    return render_template('posts/atualizar_post.html', title='Atualizar Mensagem',
                           form=form, legend='Atualizar Mensagem')


@posts.route("/<int:post_id>/excluir", methods=['POST'])
@login_required
def exclui_post(post_id):
    # Recupera o post pela ID e impede o acesso a página de 
    # todos os usuários que não sejam o autor ou um admin
    post = Post.query.filter_by(
        id=post_id).filter_by(ativo=True).first_or_404()
    if post.autor != current_user and current_user.tipo.name != 'ADMIN':
        abort(403)

    # Desativa o registro do post
    post.ativo = False
    db.session.commit()
    flash('Sua mensagem foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=2))
