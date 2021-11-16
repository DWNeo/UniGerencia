from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import current_user, login_required
from app.models import Post, Equipamento, Sala
from app.posts.forms import PostForm

principal = Blueprint('principal', __name__)


@principal.route("/")
@principal.route("/inicio")
def inicio():  
    if not current_user.is_authenticated:
        flash('É necessário realizar login para utilizar o aplicativo.', 'info')
        return redirect(url_for('users.login'))
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=1000)
    equipamentos = Equipamento.query.order_by(Equipamento.data_cadastro.desc()).paginate(page=page, per_page=1000)
    salas = Sala.query.order_by(Sala.data_cadastro.desc()).paginate(page=page, per_page=1000)

    return render_template('principal/inicio.html', posts=posts, equipamentos=equipamentos, salas=salas, form=form)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')