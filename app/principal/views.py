from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import login_required
from app.models import Post, Equipamento, Sala, Usuario
from app.posts.forms import PostForm

principal = Blueprint('principal', __name__)


@principal.route("/")
@principal.route("/inicio")
@login_required
def inicio():  
    form = PostForm()
    pagina = request.args.get('pagina', 1, type=int)
    posts = Post.query.order_by(Post.data_postado.desc())\
                .paginate(page=pagina, per_page=1000)
    equips = Equipamento.query.order_by(Equipamento.data_cadastro.desc())\
                              .paginate(page=pagina, per_page=1000)
    salas = Sala.query.order_by(Sala.data_cadastro.desc())\
                .paginate(page=pagina, per_page=1000)
    usuarios = Usuario.query.order_by(Usuario.id.desc())\
                      .paginate(page=pagina, per_page=1000)
    return render_template('principal/inicio.html', posts=posts, 
                           equipamentos=equips, salas=salas, 
                           usuarios=usuarios, form=form)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')