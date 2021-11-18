from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import current_user, login_required
from app.models import Post, Equipamento, Sala, Usuario
from app.posts.forms import PostForm

principal = Blueprint('principal', __name__)


@principal.route("/")
@principal.route("/inicio")
def inicio():  
    if not current_user.is_authenticated:
        flash('É necessário realizar login para utilizar o aplicativo.\
              Acesse a página "Sobre" para ver as contas de teste.', 'info')
        return redirect(url_for('usuarios.login'))
    form = PostForm()
    pagina = request.args.get('pagina', 1, type=int)
    posts = Post.query.order_by(Post.data_postado.desc()).paginate(page=pagina, per_page=1000)
    equipamentos = Equipamento.query.order_by(Equipamento.data_cadastro.desc()).paginate(page=pagina, per_page=1000)
    salas = Sala.query.order_by(Sala.data_cadastro.desc()).paginate(page=pagina, per_page=1000)
    usuarios = Usuario.query.order_by(Usuario.id.desc()).paginate(page=pagina, per_page=1000)
    return render_template('principal/inicio.html', posts=posts, 
                           equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, form=form)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')
