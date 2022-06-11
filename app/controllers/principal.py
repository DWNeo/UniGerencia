from flask import render_template, request, flash, Blueprint
from flask_login import current_user, login_required

from app import scheduler
from app.models import Post, Equipamento, Sala, Solicitacao, Usuario
from app.utils import enviar_email_atraso

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
        
    
@principal.context_processor
def renderizacao_tabelas():
    # Função para uso dentro do template
    def tempo_restante(solicitacao):
        tempo_restante = Solicitacao.tempo_restante(solicitacao)
        if tempo_restante:  
            return tempo_restante
        else:
            return '–––––'
    
    return dict(tempo_restante=tempo_restante)      


@principal.route("/", methods=['GET', 'POST'])
@login_required
def inicio(): 
    # Recebe o argumento sobre qual qual é a aba do menu de navegação
    # que estará ativa quando a página for aberta (padrão = 1)
    tab = request.args.get('tab', 1, type=int)
    
    # Recupera os registros ativos de cada tabela do banco de dados
    if Usuario.verificar_admin(current_user):
        solicitacoes = Solicitacao.recuperar_tudo()
        posts = Post.recuperar_tudo()
        equipamentos = Equipamento.recuperar_tudo()
        salas = Sala.recuperar_tudo()
        usuarios = Usuario.recuperar_tudo() 
    else:
        solicitacoes = Solicitacao.recuperar_tudo_autor(current_user)
        posts = Post.recuperar_tudo_autor(current_user)
        equipamentos = []
        salas = []
        usuarios = []
    
    # Verifica as solicitações por tempo restante e atrasos
    for solicitacao in solicitacoes:
        if solicitacao.verificar_confirmado():
            # Exibe uma mensagem de confirmação
            if solicitacao.verificar_autor(current_user):
                if not Usuario.verificar_admin(current_user):
                    flash('Você possui uma solicitação confirmada.', 'success')  
        if solicitacao.verificar_pendente():
            # Exibe uma mensagem de alerta para o usuário com atraso
            if solicitacao.verificar_autor(current_user):
                if not Usuario.verificar_admin(current_user):
                    flash('Você possui uma solicitação atrasada.', 'warning')  
    
    return render_template('principal/inicio.html', tab=tab, posts=posts, 
                           equipamentos=equipamentos, salas=salas, 
                           usuarios=usuarios, solicitacoes=solicitacoes)


@principal.route("/sobre")
def sobre():
    return render_template('principal/sobre.html', title='Sobre o Aplicativo')
