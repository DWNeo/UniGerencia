from datetime import datetime

from flask import jsonify, render_template, request, flash, Blueprint
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import Post, Equipamento, Sala, Solicitacao, Usuario
from app.utils import envia_email_atraso
from app.forms.solicitacoes import EntregaSolicitacaoForm

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
    solicitacoes = Solicitacao.recupera_todas()
    posts = Post.recupera_todos()
    equipamentos = Equipamento.recupera_todos()
    salas = Sala.recupera_todas()
    usuarios = Usuario.recupera_todos()
    
    # Verifica se há solicitações em uso atrasadas 
    # e atualiza o status das que estão
    for solicitacao in solicitacoes:
        if solicitacao.status.name == 'EMUSO':
            # Compara o horário atual com o previsto para devolução
            if (datetime.now().astimezone(fuso_horario) > 
                solicitacao.data_devolucao.astimezone(fuso_horario)):
                # Troca o status dos registros associados
                Solicitacao.atualiza_status_pendente(solicitacao)
                envia_email_atraso(solicitacao)

                # Exibe uma mensagem de alerta para o usuário com atraso
                if current_user == solicitacao.autor:
                    flash('Você possui uma solicitação atrasada.', 'warning')

                # Exibe uma mensagem de alerta para o admin
                if current_user.tipo.name == 'ADMIN':
                    flash('Existe uma nova solicitação em atraso.', 'warning')

    # Importa o formulário para entrega de solicitações
    # Necessário em um modal presente na tabela de solicitações
    form = EntregaSolicitacaoForm()
    
    # Renderiza a página principal
    return render_template('principal/inicio.html', tab=tab, form=form,
                           posts=posts, equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes)


@principal.route("/criar_db", methods=['GET'])
def criar_db():
    # Cria as tabelas no banco conforme as classes no models caso não existam
    db.create_all()
    db.session.commit()
    
    return 'Tabelas no banco criadas com sucesso!'


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')
