from datetime import datetime
from re import S

from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import current_user, login_required

from app import db
from app.models import (Solicitacao, Equipamento, Sala, SolicitacaoEquipamento, 
                        SolicitacaoSala, TipoEquipamento, Turno, Setor, 
                        prof_required, admin_required, Usuario)
from app.forms.solicitacoes import (SolicitacaoEquipamentoForm, TurnoForm,
                                    SolicitacaoSalaForm, EntregaSolicitacaoForm,
                                    ConfirmaSolicitacaoEquipamentoForm,
                                    ConfirmaSolicitacaoSalaForm)                          
from app.utils import envia_email_confirmacao

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/<int:solicitacao_id>")
@login_required
def solicitacao(solicitacao_id):
    # Permite acesso somente ao autor da solicitação ou a um admin
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if not solicitacao.verifica_autor(current_user):
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
    if not Usuario.verifica_prof(current_user):
        # Limita a quantidade de equipamento para alunos para 1
        form.qtd_preferencia.data = 1
        if SolicitacaoEquipamento.verifica_existente_usuario(current_user):
            flash('Você já possui uma solicitação em aberto.', 'warning')
            return redirect(url_for('principal.inicio'))
    
    # Recupera lista de turnos e tipos de equipamento do banco
    tipos_equipamento = TipoEquipamento.recupera_tudo()
    lista_tipos=[(tipo.id, tipo) for tipo in tipos_equipamento]
    turnos = Turno.recupera_tudo()
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
        if Solicitacao.verifica_inicio_hoje(form):
            # Verifica se a quantidade solicitada está disponível
            tipo_eqp = TipoEquipamento.recupera_id(form.tipo_equipamento.data)
            if form.qtd_preferencia.data > TipoEquipamento.contagem(tipo_eqp):
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
        solicitacao = SolicitacaoEquipamento.cria(status, form)  
        solicitacao.insere()
        return redirect(url_for('principal.inicio'))

    # Renderiza uma página com formulário diferente para alunos
    if not Usuario.verifica_prof(current_user):
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
    if not Usuario.verifica_prof(current_user):
        if SolicitacaoSala.verifica_existente_usuario(current_user):
            flash('Você já possui uma solicitação em aberto.', 'warning')
            return redirect(url_for('principal.inicio'))
        
    # Recupera lista de setores e turnos do banco
    setores = Setor.recupera_tudo()
    lista_setores = [(setor.id, setor) for setor in setores]
    turnos = Turno.recupera_tudo()
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
        if Solicitacao.verifica_inicio_hoje(form):
            # Verifica se a quantidade solicitada está disponível
            setor = Setor.recupera_id(form.setor.data)
            if form.qtd_preferencia.data > Setor.contagem(setor):
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
        solicitacao = SolicitacaoSala.cria(status, form)
        solicitacao.insere()
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/nova_solicitacao_sala.html', 
                           title='Nova Solicitação de Sala', 
                           legend='Nova Solicitação de Sala', form=form)


@solicitacoes.route("/<int:solicitacao_id>/confirmar", methods=['GET', 'POST'])
@login_required
@admin_required
def confirma_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    # Se a solicitação for do tipo 'Sala'...
    if solicitacao.tipo == 'SALA':
        # Preenche seletor de salas
        form = ConfirmaSolicitacaoSalaForm()
        salas = Sala.recupera_disponivel_setor(solicitacao.setor.id)
        lista_salas = [(sala.id, sala) for sala in salas]
        if lista_salas:
            form.salas.choices=lista_salas
        else:
            flash('Não há salas disponíveis no setor selecionado\
                  para confirmar.', 'warning')
            return redirect(url_for('principal.inicio'))
    
        if form.validate_on_submit():
            lista_salas = []
            # Realiza uma última verificação de disponibilidade da sala
            for sala in form.salas.data:
                sala = Sala.recupera_id(sala)
                lista_salas.append(sala)
            # Verifica se a quantidade solicitada e selecionada é igual
            if len(lista_salas) != solicitacao.quantidade:
                flash('A quantidade de salas selecionadas\
                       é diferente da solicitada.', 'warning')
                return redirect(url_for('principal.inicio'))
            # Atualiza o status da sala e da solicitação
            solicitacao.confirma(lista_salas)
            envia_email_confirmacao(solicitacao)
            flash('A solicitação foi confirmada com sucesso!', 'success')
            return redirect(url_for('principal.inicio'))

        # Preenche os campos do formulário
        elif request.method == 'GET':
            form.autor.data = solicitacao.autor.nome
            form.identificacao.data = solicitacao.autor.identificacao
            form.data_abertura.data = solicitacao.data_abertura.strftime('%d/%m/%Y')
            form.turno.data = solicitacao.turno.name
            form.setor.data = solicitacao.setor.name
            form.quantidade.data = solicitacao.quantidade
            form.qtd_disponivel.data = Setor.contagem(solicitacao.setor)
            form.data_inicio_pref.data = solicitacao.data_inicio_pref.strftime('%d/%m/%Y')
            form.data_fim_pref.data = solicitacao.data_fim_pref.strftime('%d/%m/%Y')

        return render_template('solicitacoes/confirmar_solicitacao_sala.html', 
                               title='Confirmar Solicitação de Sala', form=form,
                               legend='Confirmar Solicitação de Sala',
                               solicitacao=solicitacao)
    
    # Se a solicitação for do tipo 'Equipamento'...
    elif solicitacao.tipo == 'EQUIPAMENTO':
        # Preenche o campo de seleção de equipamentos disponíveis
        # Retorna o usuário pra tela inicial se não houver nenhum
        form = ConfirmaSolicitacaoEquipamentoForm()
        equips = Equipamento.recupera_disponivel_tipo(solicitacao.tipo_eqp_id)
        lista_equips = [(equip.id, equip) for equip in equips]
        if lista_equips:
            form.equipamentos.choices = lista_equips
        else:
            flash('Não há equipamentos disponíveis do tipo\
                  selecionado para confirmar.', 'warning')
            return redirect(url_for('principal.inicio'))
        
        if form.validate_on_submit():
            # Realiza uma última verificação de disponibilidade dos equipamentos
            # Cancela a operação caso um equipamento não esteja mais disponível
            lista_equips = []
            for eqp_id in form.equipamentos.data:
                # Adiciona cada equipamento verificado pra uma lista
                equipamento = Equipamento.recupera_id(eqp_id)
                lista_equips.append(equipamento)
            # Verifica se a quantidade solicitada e selecionada é igual
            if len(lista_equips) != solicitacao.quantidade:
                flash('A quantidade de equipamentos selecionados\
                       é diferente da solicitada.', 'warning')
                return redirect(url_for('principal.inicio'))
            # Atualiza a quantidade de equipamentos disponíveis
            solicitacao.confirma(lista_equips)
            envia_email_confirmacao(solicitacao)
            flash('A solicitação foi confirmada com sucesso!', 'success')
            return redirect(url_for('principal.inicio'))

        # Em caso de carregamento da página (GET)
        # Preenche os campos do formulário
        else:
            form.autor.data = solicitacao.autor.nome
            form.identificacao.data = solicitacao.autor.identificacao
            form.data_abertura.data = solicitacao.data_abertura.strftime('%d/%m/%Y %H:%M:%S')
            form.turno.data = solicitacao.turno
            form.tipo_equipamento.data = solicitacao.tipo_eqp.nome
            form.quantidade.data = solicitacao.quantidade
            form.qtd_disponivel.data = TipoEquipamento.contagem(solicitacao.tipo_eqp)
            form.equipamentos.data = solicitacao.equipamentos
            form.data_inicio_pref.data = solicitacao.data_inicio_pref.strftime('%d/%m/%Y')
            form.data_fim_pref.data = solicitacao.data_fim_pref.strftime('%d/%m/%Y')

        return render_template('solicitacoes/confirmar_solicitacao_equipamento.html', 
                               title='Confirmar Solicitação de Equipamento', 
                               form=form, solicitacao=solicitacao,
                               legend='Confirmar Solicitação de Equipamento')


@solicitacoes.route("/<int:solicitacao_id>/entregar", methods=['GET', 'POST'])
@login_required
@admin_required
def entrega_solicitacao(solicitacao_id):
    # Permite a entrega somente de solicitações confirmadas
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if not solicitacao.verifica_confirmado():
        flash('Esta solicitação não foi confirmada!', 'warning')
        return redirect(url_for('principal.inicio'))

    form = EntregaSolicitacaoForm()
    if form.validate_on_submit():
        # Altera o status da sala/equipamentos associados para 'Em Uso'
        solicitacao.em_uso(form)
        flash('A entrega foi confirmada com sucesso!', 'success')
    else:
        flash('A data de devolução inserida é inválida.', 'warning')

    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/receber", methods=['GET', 'POST'])
@login_required
@admin_required
def recebe_solicitacao(solicitacao_id):
    # Verifica o status da solicitação para permitir seu recebimento 
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if not (solicitacao.verifica_em_uso() or solicitacao.verifica_pendente()):
        flash('Esta solicitação não está em uso!', 'warning')
        return redirect(url_for('principal.inicio'))
    
    # Atualiza o registro da solicitação
    solicitacao.finaliza()
    flash('O recebimento foi confirmado com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/cancelar", methods=['POST'])
@login_required
def cancela_solicitacao(solicitacao_id):
    # Permite acesso somente ao autor da solicitação ou a um admin
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if not solicitacao.verifica_autor(current_user):
        abort(403)

    # Verifica o status da solicitação para permitir seu cancelamento
    if (solicitacao.verifica_em_uso() or solicitacao.verifica_pendente()):
        flash('Esta solicitação não pode ser mais cancelada!', 'warning')
        return redirect(url_for('principal.inicio'))

    # Altera o status de sala/equipamentos associados a solicitação
    solicitacao.cancela()
    flash('A solicitação foi cancelada com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_solicitacao(solicitacao_id):
    # Impede a exclusão de solicitações indevidas
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if (solicitacao.verifica_em_uso() or solicitacao.verifica_pendente()):
        flash('Não é possível excluir uma solicitação em uso.', 'warning')
        return redirect(url_for('principal.inicio'))
    
    # Atualiza o status dos equipamentos e salas antes de excluir a solicitação
    solicitacao.exclui()
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
        turno = Turno.cria(form)
        turno.insere()
        flash('O turno foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/novo_turno.html', 
                           title='Novo Turno',
                           legend='Novo Turno', form=form)
    