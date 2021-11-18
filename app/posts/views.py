from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required

from app import db
from app.models import Post
from app.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts/post.html', title=post.titulo, post=post)


@posts.route("/novo", methods=['GET', 'POST'])
@login_required
def novo_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, 
                    conteudo=form.conteudo.data, 
                    autor=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Sua mensagem foi postada com sucesso!', 'success')
        return redirect(url_for('principal.inicio'))
    return render_template('posts/novo_post.html', title='Novo Post',
                           form=form, legend='Novo Post')


@posts.route("/<int:post_id>/atualizar", methods=['GET', 'POST'])
@login_required
def atualiza_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.autor != current_user and current_user.admin == False:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.titulo = form.titulo.data
        post.conteudo = form.conteudo.data
        db.session.commit()
        flash('Seu post foi atualizado com sucesso!', 'success')
        return redirect(url_for('principal.inicio'))
    elif request.method == 'GET':
        form.titulo.data = post.titulo
        form.conteudo.data = post.conteudo
    return render_template('posts/novo_post.html', title='Atualizar Post',
                           form=form, legend='Atualizar Post')


@posts.route("/<int:post_id>/excluir", methods=['POST'])
@login_required
def exclui_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.autor != current_user and current_user.admin == False:
        abort(403)
    post.ativo = False
    db.session.commit()
    flash('Seu post foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))