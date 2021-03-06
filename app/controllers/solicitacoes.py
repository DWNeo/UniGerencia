
from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import current_user, login_required

from app.models import (Solicitacao, Equipamento, Sala, SolicitacaoEquipamento, 
                        SolicitacaoSala, TipoEquipamento, Turno, Setor, 
                        Usuario, prof_required, admin_required)
from app.forms.solicitacoes import (SolicitacaoEquipamentoForm, TurnoForm,
                                    SolicitacaoSalaForm,
                                    EntregaSolicitacaoEquipamentoForm,
                                    EntregaSolicitacaoSalaForm)                          
from app.utils import enviar_email_confirmacao

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/<int:solicitacao_id>", methods=['GET'])
@login_required
def solicitacao(solicitacao_id):
    # Permite acesso somente ao autor da solicitação ou a um admin
    solicitacao = Solicitacao.recuperar_id(solicitacao_id)
    if not solicitacao.verificar_autor(current_user):
        abort(403)
    # Calcula o tempo restante para uma solitação
    tempo_restante= solicitacao.tempo_restante()

    return render_template('solicitacoes/solicitacao.html', 
                           title=solicitacao, solicitacao=solicitacao,
                           tempo_restante=tempo_restante)


@solicitacoes.route("/nova/equipamento", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_equipamento():
    # Impede um usuário de realizar mais de uma solicitação por vez
    form = SolicitacaoEquipamentoForm()
    if not Usuario.verificar_prof(current_user):
        # Limita a quantidade de equipamento para alunos para 1
        form.qtd_preferencia.data = 1
        if SolicitacaoEquipamento.verificar_existente_usuario(current_user):
            flash('Você já possui uma solicitação em aberto.', 'warning')
            return redirect(url_for('principal.inicio'))
    
    # Recupera lista de turnos e tipos de equipamento do banco
    tipos_equipamento = TipoEquipamento.recuperar_tudo()
    lista_tipos=[(tipo.id, tipo) for tipo in tipos_equipamento]
    turnos = Turno.recuperar_tudo()
    lista_turnos = [(turno.id, turno) for turno in turnos]
    
    # Preenche as listas de seleção
    # Retorna usuário pra tela inicial se não há dados cadastrados
    if lista_tipos and lista_turnos:
        form.tipo_equipamento.choices = lista_tipos
        form.turno.choices = lista_turnos
    else:
        flash('Não há tipos ou turnos cadastrados para solicitar equipamentos.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit(): 
        # Define o status de acordo com a data de início preferencial
        if Solicitacao.verificar_inicio_hoje(form.data_inicio_pref.data):
            # Verifica se a quantidade solicitada está disponível
            tipo_eqp = TipoEquipamento.recuperar_id(form.tipo_equipamento.data)
            if form.qtd_preferencia.data > TipoEquipamento.contar(tipo_eqp):
                flash('Não há equipamentos suficientes do tipo escolhido.\
                    Favor escolher uma quantidade menor.', 'warning')
                return redirect(url_for('principal.inicio'))
            else:
                status = 'SOLICITADO'
                flash('A solicitação foi realizada com sucesso!.', 'success')    
        else:
            status = 'ABERTO'
            flash('Você foi colocado na lista de espera pois\
                   escolheu outro dia como preferência.', 'warning')     
        
        # Insere a nova solicitação no banco de dados
        solicitacao = SolicitacaoEquipamento.criar(status, form)  
        solicitacao.inserir()
        return redirect(url_for('principal.inicio'))

    # Renderiza uma página com formulário diferente para alunos
    if not Usuario.verificar_prof(current_user):
        return render_template('solicitacoes/nova_solicitacao_equipamento_aluno.html', 
                               title='Nova Solicitação de Equipamento', form=form,
                               legend='Nova Solicitação de Equipamento')
    else:
        return render_template('solicitacoes/nova_solicitacao_equipamento.html', 
                               title='Nova Solicitação de Equipamento', form=form,
                               legend='Nova Solicitação de Equipamento')


@solicitacoes.route("/nova/sala", methods=['GET', 'POST'])
@login_required
@prof_required
def nova_solicitacao_sala():
    # Impede um usuário de realizar mais de uma solicitação por vez
    if not Usuario.verificar_prof(current_user):
        if SolicitacaoSala.verificar_existente_usuario(current_user):
            flash('Você já possui uma solicitação em aberto.', 'warning')
            return redirect(url_for('principal.inicio'))
        
    # Recupera lista de setores e turnos do banco
    setores = Setor.recuperar_tudo()
    lista_setores = [(setor.id, setor) for setor in setores]
    turnos = Turno.recuperar_tudo()
    lista_turnos = [(turno.id, turno) for turno in turnos]
    
    # Preenche as listas de seleção
    # Retorna usuário pra tela inicial se não dados cadastrados
    form = SolicitacaoSalaForm()
    if lista_setores and lista_turnos:
        form.setor.choices = lista_setores
        form.turno.choices = lista_turnos
    else:
        flash('Não há setores ou turnos cadastrados para solicitar salas.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        # Define o status de acordo com a data de início preferencial
        if Solicitacao.verificar_inicio_hoje(form.data_inicio_pref.data):
            # Verifica se a quantidade solicitada está disponível
            setor = Setor.recuperar_id(form.setor.data)
            if form.qtd_preferencia.data > Setor.contar(setor):
                flash('Não há salas suficientes no setor escolhido.\
                    Favor escolher uma quantidade menor.', 'warning')
                return redirect(url_for('principal.inicio')) 
            else:
                status = 'SOLICITADO'
                flash('A solicitação foi realizada com sucesso!.', 'success')     
        else:
            status = 'ABERTO'
            flash('Você foi colocado na lista de espera pois\
                   escolheu outro dia como preferência.', 'warning')
        # Insere a nova solicitação no banco de dados
        solicitacao = SolicitacaoSala.criar(status, form)
        solicitacao.inserir()
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/nova_solicitacao_sala.html', 
                           title='Nova Solicitação de Sala', 
                           legend='Nova Solicitação de Sala', form=form)


@solicitacoes.route("/<int:solicitacao_id>/confirmar", methods=['POST'])
@login_required
@admin_required
def confirma_solicitacao(solicitacao_id):
    # Atualiza o status da solicitação
    solicitacao = Solicitacao.recuperar_id(solicitacao_id)
    if not solicitacao.verificar_aberto():
        flash('Esta solicitação não está em aberto!', 'warning')
        return redirect(url_for('principal.inicio'))
    solicitacao.confirmar()
    enviar_email_confirmacao(solicitacao)
    flash('A solicitação foi confirmada com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/entregar", methods=['GET', 'POST'])
@login_required
@admin_required
def entrega_solicitacao(solicitacao_id):
    # Permite a entrega somente de solicitações confirmadas
    solicitacao = Solicitacao.recuperar_id(solicitacao_id)
    if not solicitacao.verificar_confirmado():
        flash('Esta solicitação não foi confirmada!', 'warning')
        return redirect(url_for('principal.inicio'))
    # Preenche o campo de seleção de itens disponíveis
    if solicitacao.tipo == 'EQUIPAMENTO':
        form = EntregaSolicitacaoEquipamentoForm()
        equips = Equipamento.recuperar_disponivel_tipo(solicitacao.tipo_eqp_id)
        lista_equips = [(equip.id, equip) for equip in equips]
        if lista_equips:
            form.equipamentos.choices = lista_equips
        else:
            flash('Não há equipamentos disponíveis do tipo\
                    selecionado.', 'warning')
            return redirect(url_for('principal.inicio'))
    elif solicitacao.tipo == 'SALA':
        form = EntregaSolicitacaoSalaForm()
        salas = Sala.recuperar_disponivel_setor(solicitacao.setor.id)
        lista_salas = [(sala.id, sala) for sala in salas]
        if lista_salas:
            form.salas.choices=lista_salas
        else:
            flash('Não há salas disponíveis no setor\
                  selecionado.', 'warning')
            return redirect(url_for('principal.inicio'))
        
    if form.validate_on_submit():
        # Realiza uma última verificação de disponibilidade dos itens
        if solicitacao.tipo == 'EQUIPAMENTO':
            lista_equips = []
            for eqp_id in form.equipamentos.data:
                equipamento = Equipamento.recuperar_aberto_id(eqp_id)
                lista_equips.append(equipamento)
            if len(lista_equips) == 0:
                flash('Os equipamentos selecionados não estão\
                      mais disponíveis.', 'warning')
                return redirect(url_for('principal.inicio'))
            solicitacao.entregar(lista_equips, form)
        elif solicitacao.tipo == 'SALA':
            lista_salas = []
            for sala in form.salas.data:
                sala = Sala.recuperar_aberto_id(sala)
                lista_salas.append(sala)
            if len(lista_salas) == 0:
                flash('As salas selecionadas não estão\
                      mais disponíveis.', 'warning')
                return redirect(url_for('principal.inicio'))
            solicitacao.entregar(lista_salas, form)
        flash('A entrega foi confirmada com sucesso!', 'success')
        return redirect(url_for('principal.inicio'))
    else:
        if solicitacao.tipo == 'EQUIPAMENTO':
            form.tipo_equipamento.data = solicitacao.tipo_eqp
        elif solicitacao.tipo == 'SALA':
            form.setor.data = solicitacao.setor
        form.autor.data = solicitacao.autor
        form.data_abertura.data = solicitacao.data_abertura.strftime('%d/%m/%Y %H:%M:%S')
        form.descricao.data = solicitacao.descricao
        form.turno.data = solicitacao.turno
        form.quantidade.data = solicitacao.quantidade
        form.data_inicio_pref.data = solicitacao.data_inicio_pref.strftime('%d/%m/%Y')
        form.data_fim_pref.data = solicitacao.data_fim_pref.strftime('%d/%m/%Y')  
        form.data_devolucao.data = solicitacao.data_fim_pref
    
    # Renderiza template de acordo com o tipo de solicitação
    if solicitacao.tipo == 'EQUIPAMENTO':
        return render_template('solicitacoes/entregar_solicitacao_equipamento.html', 
                            title='Entregar Solicitação de Equipamento', 
                            legend='Entregar Solicitação de Equipamento',
                            form=form, solicitacao=solicitacao)
    elif solicitacao.tipo == 'SALA':
        return render_template('solicitacoes/entregar_solicitacao_sala.html', 
                            title='Entregar Solicitação de Sala', 
                            legend='Entregar Solicitação de Sala',
                            form=form, solicitacao=solicitacao)

@solicitacoes.route("/<int:solicitacao_id>/receber", methods=['GET', 'POST'])
@login_required
@admin_required
def recebe_solicitacao(solicitacao_id):
    # Verifica o status da solicitação para permitir seu recebimento 
    solicitacao = Solicitacao.recuperar_id(solicitacao_id)
    if not (solicitacao.verificar_em_uso() or solicitacao.verificar_pendente()):
        flash('Esta solicitação não está em uso!', 'warning')
        return redirect(url_for('principal.inicio'))
    # Atualiza o registro da solicitação
    solicitacao.finalizar()
    flash('O recebimento foi confirmado com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/cancelar", methods=['POST'])
@login_required
def cancela_solicitacao(solicitacao_id):
    # Permite acesso somente ao autor da solicitação ou a um admin
    solicitacao = Solicitacao.recuperar_id(solicitacao_id)
    if not solicitacao.verificar_autor(current_user):
        abort(403)
    # Verifica o status da solicitação para permitir seu cancelamento
    if (solicitacao.verificar_em_uso() or solicitacao.verificar_pendente()):
        flash('Esta solicitação não pode ser mais cancelada!', 'warning')
        return redirect(url_for('principal.inicio'))
    # Altera o status de sala/equipamentos associados a solicitação
    solicitacao.cancelar()
    flash('A solicitação foi cancelada com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_solicitacao(solicitacao_id):
    # Impede a exclusão de solicitações indevidas
    solicitacao = Solicitacao.recuperar_id(solicitacao_id)
    if (solicitacao.verificar_em_uso() or solicitacao.verificar_pendente()):
        flash('Não é possível excluir uma solicitação em uso.', 'warning')
        return redirect(url_for('principal.inicio'))
    # Atualiza o status dos equipamentos e salas antes de excluir a solicitação
    solicitacao.excluir()
    flash('A solicitação foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/novo_turno", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_turno():
    # Valida os dados do formulário enviado e insere um 
    # novo registro de turno no banco de dados
    form = TurnoForm()
    if form.validate_on_submit():
        turno = Turno.criar(form)
        turno.inserir()
        flash('O turno foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/novo_turno.html', 
                           title='Novo Turno',
                           legend='Novo Turno', form=form)
    