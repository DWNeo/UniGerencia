from datetime import datetime

from flask import render_template, request, flash, Blueprint
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import Post, Equipamento, Sala, Usuario, Solicitacao

principal = Blueprint('principal', __name__)


@principal.route("/")
@login_required
def inicio(): 
    # Recebe o argumento sobre qual qual é a aba do menu de navegação
    # que estará ativa quando a página for aberta (padrão = 1)
    tab = request.args.get('tab', 1, type=int)

    # Recupera os registros ativos de cada tabela do banco de dados
    # A paginação pode ser necessária caso haja uma expectativa
    # de número de dados grandes o suficiente
    solicitacoes = Solicitacao.query.filter_by(ativo=True).all()
    posts = Post.query.filter_by(ativo=True).all()
    equipamentos = Equipamento.query.filter_by(ativo=True).all()
    salas = Sala.query.filter_by(ativo=True).all()
    usuarios = Usuario.query.filter_by(ativo=True).all()

    print(len(equipamentos))
    
    # Verifica se há solicitações em uso atrasadas 
    # e atualiza o status das que estão
    for solicitacao in solicitacoes:
        if solicitacao.status == 'Em Uso':
            # Compara o horário atual com o previsto para devolução
            if (datetime.now().astimezone(fuso_horario) > 
                solicitacao.data_devolucao.astimezone(fuso_horario)):
                # Troca o status dos registros associados
                solicitacao.status = 'Em Atraso'
                if solicitacao.equipamento:
                    solicitacao.equipamento.status = 'Em Atraso'
                if solicitacao.sala:
                    solicitacao.sala.status = 'Em Atraso'
                db.session.commit()

                # Exibe uma mensagem de alerta para o usuário com atraso
                if current_user == solicitacao.autor:
                    flash('Você possui uma solicitação atrasada.', 'warning')

                # Exibe uma mensagem de alerta para o admin
                if current_user.admin == True:
                    flash('Existe uma nova solicitação em atraso.', 'warning')

    # Renderiza o template
    return render_template('principal/inicio.html', tab=tab,
                           posts=posts, equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')