from datetime import datetime

from flask import render_template, request, flash, Blueprint
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import Post, Equipamento, Sala, Usuario, Solicitacao
from app.usuarios.utils import envia_email_atraso
from app.solicitacoes.forms import EntregaSolicitacaoForm

principal = Blueprint('principal', __name__)


@principal.route("/", methods=['GET', 'POST'])
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
    
    # Verifica se há solicitações em uso atrasadas 
    # e atualiza o status das que estão
    for solicitacao in solicitacoes:
        if solicitacao.status == 'EMUSO':
            # Compara o horário atual com o previsto para devolução
            if (datetime.now().astimezone(fuso_horario) > 
                solicitacao.data_devolucao.astimezone(fuso_horario)):
                # Troca o status dos registros associados
                solicitacao.status = 'PENDENTE'
                if solicitacao.equipamentos:
                    for equipamento in solicitacao.equipamentos:
                        equipamento.status = 'PENDENTE'
                if solicitacao.sala:
                    solicitacao.sala.status = 'PENDENTE'
                db.session.commit()
                envia_email_atraso(solicitacao)

                # Exibe uma mensagem de alerta para o usuário com atraso
                if current_user == solicitacao.autor:
                    flash('Você possui uma solicitação atrasada.', 'warning')

                # Exibe uma mensagem de alerta para o admin
                if current_user.admin == True:
                    flash('Existe uma nova solicitação em atraso.', 'warning')

    # Importa o formulário para entrega de solicitações
    # Necessário em um modal presente na tabela de solicitações
    form = EntregaSolicitacaoForm()
    # Renderiza o template
    return render_template('principal/inicio.html', tab=tab, form=form,
                           posts=posts, equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')