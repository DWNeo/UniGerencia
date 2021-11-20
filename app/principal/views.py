from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import login_required

from app.models import Post, Equipamento, Sala, Usuario, Solicitacao

principal = Blueprint('principal', __name__)


@principal.route("/")
@login_required
def inicio():  
    # Recupera os registros ativos de cada tabela do banco de dados
    solicitacoes = Solicitacao.query.filter_by(ativo=True).all()
    posts = Post.query.filter_by(ativo=True).all()
    equipamentos = Equipamento.query.filter_by(ativo=True).all()
    salas = Sala.query.filter_by(ativo=True).all()
    usuarios = Usuario.query.filter_by(ativo=True).all()
    return render_template('principal/inicio.html', posts=posts, 
                           equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')