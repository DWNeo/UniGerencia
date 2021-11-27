from datetime import datetime

from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required

from app import db, fuso_horario
from app.models import Post
from app.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/<int:post_id>")
@login_required
def post(post_id):
    # Recupera o post pela ID
    post = Post.query.filter_by(
        id=post_id).filter_by(ativo=True).first_or_404()

    # Renderiza o template
    return render_template('posts/post.html', title=post.titulo, post=post)


@posts.route("/novo", methods=['GET', 'POST'])
@login_required
def novo_post():
    # Valida os dados do formulário enviado e insere um 
    # novo registro de post no banco de dados
    form = PostForm()
    if form.validate_on_submit():
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

    # Impede o acesso a página de todos os usuários que 
    # não sejam o autor do post ou um admin
    if post.autor != current_user and current_user.admin == False:
        abort(403)
    
    # Valida o formulário enviado e atualiza o registro
    # do post no banco de dados de acordo com ele
    form = PostForm()
    if form.validate_on_submit():
        post.titulo = form.titulo.data
        post.conteudo = form.conteudo.data
        post.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        flash('Sua mensagem foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=2))
    elif request.method == 'GET':
        form.titulo.data = post.titulo
        form.conteudo.data = post.conteudo

    return render_template('posts/novo_post.html', title='Atualizar Mensagem',
                           form=form, legend='Atualizar Mensagem')


@posts.route("/<int:post_id>/excluir", methods=['POST'])
@login_required
def exclui_post(post_id):
    # Recupera o post pela ID e impede o acesso a página de 
    # todos os usuários que não sejam o autor ou um admin
    post = Post.query.filter_by(
        id=post_id).filter_by(ativo=True).first_or_404()
    if post.autor != current_user and current_user.admin == False:
        abort(403)

    # Desativa o registro do post
    post.ativo = False
    db.session.commit()
    flash('Sua mensagem foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=2))