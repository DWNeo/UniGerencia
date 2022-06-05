from datetime import datetime

from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import current_user, login_required

from app import db, fuso_horario
from app.models import (Solicitacao, Equipamento, Sala, SolicitacaoEquipamento, 
                        SolicitacaoSala, TipoEquipamento, Turno, Setor, 
                        prof_required, admin_required)
from app.forms.solicitacoes import (SolicitacaoEquipamentoForm, TurnoForm,
                                    SolicitacaoSalaForm, EntregaSolicitacaoForm,
                                    ConfirmaSolicitacaoEquipamentoForm,
                                    ConfirmaSolicitacaoSalaForm)
from app.models.usuarios import Usuario                            
from app.utils import envia_email_confirmacao

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/<int:solicitacao_id>")
@login_required
def solicitacao(solicitacao_id):
    # Permite acesso somente ao autor da solicitação ou a um admin
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if not Solicitacao.verifica_autor(solicitacao, current_user):
        abort(403)

    return render_template('solicitacoes/solicitacao.html', 
                           title=solicitacao, solicitacao=solicitacao)


@solicitacoes.route("/nova/equipamento", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_equipamento():
    # Recupera lista de turnos e tipos de equipamento do banco
    tipos_equipamento = TipoEquipamento.recupera_tudo()
    lista_tipos=[(tipo.id, tipo) for tipo in tipos_equipamento]
    turnos = Turno.recupera_tudo()
    lista_turnos = [(turno.id, turno) for turno in turnos]
    
    # Preenche as listas de seleção
    # Retorna usuário pra tela inicial se não dados cadastrados
    form = SolicitacaoEquipamentoForm()
    if lista_tipos and lista_turnos:
        form.tipo_equipamento.choices = lista_tipos
        form.turno.choices = lista_turnos
    else:
        flash('Não há tipos ou turnos cadastrados para solicitar equipamentos.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        ''' [Em Verificação]
        solicitacao = SolicitacaoEquipamento.query.filter_by(
            status='ABERTO').filter_by(
            turno_id=form.turno.data).filter_by(ativo=True).first()
        '''   
        # Verifica se há equipamentos disponíveis para a quantidade solicitada
        # Retorna a operação caso não haja equipamentos o suficiente
        tipo_eqp = TipoEquipamento.recupera_id(form.tipo_equipamento.data)
        if form.qtd_preferencia.data > TipoEquipamento.contagem(tipo_eqp):
            flash('A quantidade solicitada de equipamentos excede a disponível.\
                   Por favor, insira um valor menor.', 'warning')
            return redirect(url_for('principal.inicio'))
        else:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'ABERTO'
        ''' [Em Verificação]
        elif solicitacao:
            flash('Você foi colocado na lista de espera pois o equipamento\
                  escolhido não está disponível.', 'warning')
            status = 'SOLICITADO'
        '''
        # Insere a nova solicitação no banco de dados
        solicitacao = SolicitacaoEquipamento.cria(status, form)
        SolicitacaoEquipamento.insere(solicitacao)
        flash('A solicitação foi realizada com sucesso!.', 'success')
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/nova_solicitacao_equipamento.html', 
                           title='Nova Solicitação de Equipamento', form=form,
                           legend='Nova Solicitação de Equipamento')


@solicitacoes.route("/nova/sala", methods=['GET', 'POST'])
@login_required
@prof_required
def nova_solicitacao_sala():
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
        setor = Setor.recupera_id(form.setor.data)
        ''' [EM VERIFICAÇÃO]
        solicitacao = SolicitacaoSala.query.filter_by(turno_id=form.turno.data).filter_by(
                status='ABERTO').filter_by(ativo=True).first()
        '''
        solicitacao = None
        # Verifica se a sala solicitada está disponível
        # Muda o status da solicitação de acordo com o resultado
        if Setor.contagem(setor) == 0:
            flash('Não há salas disponíveis neste setor para solicitar.', 'warning')
            return redirect(url_for('principal.inicio'))
        if Setor.contagem(setor) >= form.qtd_preferencia.data and solicitacao == None:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'ABERTO'
        else:
            flash('Você foi colocado na lista de espera pois o setor\
                  escolhido não possui salas disponíveis.', 'warning')
            status = 'SOLICITADO'
               
        # Insere a nova solicitação no banco de dados
        solicitacao = SolicitacaoSala.cria(status, form)
        SolicitacaoSala.insere(solicitacao)
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
            flash('Não há salas disponíveis para confirmar.', 'warning')
            return redirect(url_for('principal.inicio'))
        
        if form.validate_on_submit():
            lista_salas = []
            for sala in form.salas.data:
                sala = Sala.query.filter_by(id=sala).filter_by(ativo=True).first()
                # Realiza uma última verificação de disponibilidade da sala
                # Cancela a operação caso a sala não esteja mais disponível
                if sala == None:                    
                    flash('Uma sala não está mais disponível.', 'warning')
                    return redirect(url_for('principal.inicio'))
                lista_salas.append(sala)
            solicitacao.salas = lista_salas
            if len(solicitacao.salas) != solicitacao.quantidade:
                flash('A quantidade de salas selecionadas\
                       é diferente da solicitada.', 'warning')
                return redirect(url_for('principal.inicio'))
            
            # Atualiza status das salas da solicitação
            for sala in lista_salas:
                sala.status = 'CONFIRMADO'
            
            # Atualiza o status da sala e da solicitação
            solicitacao.setor.qtd_disponivel -= len(solicitacao.salas)
            solicitacao.status = 'CONFIRMADO'
            db.session.commit()
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
        equips = Equipamento.query.filter_by(status='ABERTO').filter_by(
            ativo=True).filter_by(tipo_eqp_id=solicitacao.tipo_eqp_id).all()
        lista_equips = [(equip.id, equip) for equip in equips]
        if lista_equips:
            form.equipamentos.choices = lista_equips
        else:
            flash('Não há equipamentos disponíveis para confirmar.', 'warning')
            return redirect(url_for('principal.inicio'))

        # Em caso de envio de formulário (POST)
        if form.validate_on_submit():
            # Realiza uma última verificação de disponibilidade dos equipamentos
            # Cancela a operação caso um equipamento não esteja mais disponível
            lista_equips = []
            for eqp_id in form.equipamentos.data:
                equipamento = Equipamento.query.filter_by(
                    id=eqp_id).filter_by(
                    status='ABERTO').filter_by(ativo=True).first()
                if equipamento == None:
                    flash('Um equipamento não está mais disponível.', 'warning')
                    return redirect(url_for('principal.inicio'))
                # Adiciona cada equipamento verificado pra uma lista
                lista_equips.append(equipamento)

            # Associa os equipamentos da lista à solicitação
            solicitacao.equipamentos = lista_equips

            # Verifica se a quantidade de equipamentos selecionados pelo
            # admin é igual a quantidade solicitada
            if len(solicitacao.equipamentos) != solicitacao.quantidade:
                flash('A quantidade de equipamentos selecionados\
                       é diferente da solicitada.', 'warning')
                return redirect(url_for('principal.inicio'))

            # Atualiza status dos equipamentos da solicitação
            for equip in lista_equips:
                equip.status = 'CONFIRMADO'

            # Atualiza a quantidade de equipamentos disponíveis
            solicitacao.tipo_eqp.qtd_disponivel -= len(solicitacao.equipamentos)
            solicitacao.status = 'CONFIRMADO'
            db.session.commit()
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
    if solicitacao.status.name != 'CONFIRMADO':
        flash('Esta solicitação não foi confirmada!', 'warning')
        return redirect(url_for('principal.inicio'))

    form = EntregaSolicitacaoForm()
    if form.validate_on_submit():
        # Altera o status da sala/equipamentos associados para 'Em Uso'
        Solicitacao.em_uso(solicitacao, form)
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
    if not Solicitacao.verifica_em_uso(solicitacao):
        flash('Esta solicitação não está em uso!', 'warning')
        return redirect(url_for('principal.inicio'))
    
    # Atualiza o registro da solicitação
    Solicitacao.finaliza(solicitacao)
    flash('O recebimento foi confirmado com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/cancelar", methods=['POST'])
@login_required
def cancela_solicitacao(solicitacao_id):
    # Permite acesso somente ao autor da solicitação ou a um admin
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if not Solicitacao.verifica_autor(solicitacao, current_user):
        abort(403)

    # Verifica o status da solicitação para permitir seu cancelamento
    if Solicitacao.verifica_em_uso(solicitacao):
        flash('Esta solicitação não pode ser mais cancelada!', 'warning')
        return redirect(url_for('principal.inicio'))

    # Altera o status de sala/equipamentos associados a solicitação
    Solicitacao.cancela(solicitacao)
    flash('A solicitação foi cancelada com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_solicitacao(solicitacao_id):
    # Impede a exclusão de solicitações indevidas
    solicitacao = Solicitacao.recupera_id(solicitacao_id)
    if Solicitacao.verifica_em_uso(solicitacao):
        flash('Não é possível excluir uma solicitação em uso.', 'warning')
        return redirect(url_for('principal.inicio'))
    
    # Atualiza o status dos equipamentos e salas antes de excluir a solicitação
    Solicitacao.exclui(solicitacao)
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
        Turno.insere(turno)
        flash('O turno foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/novo_turno.html', 
                           title='Novo Turno',
                           legend='Novo Turno', form=form)
    