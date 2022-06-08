from flask import render_template, request, flash, Blueprint
from flask_login import current_user, login_required

from app import db, scheduler
from app.controllers.equipamentos import equipamento
from app.models import Post, Equipamento, Sala, Solicitacao, Usuario
from app.utils import enviar_email_atraso
from app.forms.solicitacoes import EntregaSolicitacaoForm

principal = Blueprint('principal', __name__)

# Tarefa que roda no fundo para atualizar os status da solicitações
@scheduler.task('interval', id='atualiza_status', seconds=60, misfire_grace_time=900)
def atualiza_status_solicitacoes():
    with scheduler.app.app_context(): 
        print('Scheduler: Atualizando status das solicitações...')
        # Verifica se há solicitações em uso atrasadas 
        solicitacoes = Solicitacao.recuperar_em_uso()
        for solicitacao in solicitacoes:
            if solicitacao.verificar_atraso():
                # Atualiza o status das solicitações que estão
                solicitacao.pendente()
                print('Scheduler: Existe uma nova solicitação atrasada.')
                print('Scheduler: ', solicitacao)
                enviar_email_atraso(solicitacao)
        # Verifica se há solicitações marcadas o dia atual     
        solicitacoes = Solicitacao.recuperar_aberto()
        for solicitacao in solicitacoes:
            if solicitacao.verificar_inicio_hoje():
                # Atualiza o status das solicitações que estão
                solicitacao.solicitado()
                print('Scheduler: Existe uma nova solicitação para hoje.')
                print('Scheduler: ', solicitacao)
                        

@principal.route("/", methods=['GET', 'POST'])
@login_required
def inicio(): 
    # Recebe o argumento sobre qual qual é a aba do menu de navegação
    # que estará ativa quando a página for aberta (padrão = 1)
    tab = request.args.get('tab', 1, type=int)
    
    # Recupera os registros ativos de cada tabela do banco de dados
    solicitacoes = Solicitacao.recuperar_tudo()
    posts = Post.recuperar_tudo()
    equipamentos = Equipamento.recuperar_tudo()
    salas = Sala.recuperar_tudo()
    usuarios = Usuario.recuperar_tudo() 
    
    # Verifica as solicitações por tempo restante e atrasos
    lista_tempo = []
    for solicitacao in solicitacoes:
        tempo_restante = solicitacao.tempo_restante()
        lista_tempo.append(tempo_restante) 
        if solicitacao.verificar_pendente():
            # Exibe uma mensagem de alerta para o usuário com atraso
            if solicitacao.verificar_autor(current_user):
                if not Usuario.verificar_admin(current_user):
                    flash('Você possui uma solicitação atrasada.', 'warning')  

    # Importa o formulário para entrega de solicitações
    # Necessário em um modal presente na tabela de solicitações
    form = EntregaSolicitacaoForm()
    
    return render_template('principal/inicio.html', tab=tab, form=form,
                           posts=posts, equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes,
                           tempo_restante=lista_tempo)


@principal.route("/criar_db", methods=['GET'])
def criar_db():
    # Cria as tabelas no banco conforme as classes no models caso não existam
    db.create_all()
    db.session.commit()
    return 'Tabelas no banco criadas com sucesso!'


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')
