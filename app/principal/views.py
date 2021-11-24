from datetime import datetime

from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import Post, Equipamento, Sala, Usuario, Solicitacao

principal = Blueprint('principal', __name__)


@principal.route("/")
@login_required
def inicio(): 
    tab = request.args.get('tab', 1, type=int)
    # Recupera os registros ativos de cada tabela do banco de dados
    solicitacoes = Solicitacao.query.filter_by(ativo=True).all()
    posts = Post.query.filter_by(ativo=True).all()
    equipamentos = Equipamento.query.filter_by(ativo=True).all()
    salas = Sala.query.filter_by(ativo=True).all()
    usuarios = Usuario.query.filter_by(ativo=True).all()
    
    # Verifica se as solicitações em uso estão atrasadas
    # e atualiza os status das solicitações em questão
    for solicitacao in solicitacoes:
        if solicitacao.status == 'Em Uso':
            if datetime.now().astimezone(fuso_horario) > solicitacao.data_devolucao.astimezone(fuso_horario):
                solicitacao.status = 'Em Atraso'
                if solicitacao.equipamento:
                    solicitacao.equipamento.status = 'Em Atraso'
                if solicitacao.sala:
                    solicitacao.sala.status = 'Em Atraso'
                db.session.commit()
                if current_user.admin == True:
                    flash('Existe uma nova solicitação em atraso.', 'warning')

    return render_template('principal/inicio.html', tab=tab,
                           posts=posts, equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')