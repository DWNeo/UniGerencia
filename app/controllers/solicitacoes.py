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
from app.utils import envia_email_confirmacao

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/<int:solicitacao_id>")
@login_required
def solicitacao(solicitacao_id):
    # Recupera a sala pela ID
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()

    # Permite acesso somente ao autor da solicitação ou a um admin
    if solicitacao.autor != current_user and current_user.tipo.name != 'ADMIN':
        abort(403)

    # Renderiza o template
    return render_template('solicitacoes/solicitacao.html', 
                           title=solicitacao, solicitacao=solicitacao)


@solicitacoes.route("/nova/equipamento", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_equipamento():
    # Recupera lista de turnos e tipos de equipamento do banco
    form = SolicitacaoEquipamentoForm()
    tipos_equipamento = TipoEquipamento.query.filter_by(ativo=True).all()
    lista_tipos=[(tipo.id, tipo) for tipo in tipos_equipamento]
    turnos = Turno.query.filter_by(ativo=True).all()
    lista_turnos = [(turno.id, turno) for turno in turnos]
    
    # Preenche as listas de seleção
    if lista_tipos and lista_turnos:
        form.tipo_equipamento.choices = lista_tipos
        form.turno.choices = lista_turnos
    else:
        flash('Não há tipos ou turnos cadastrados para solicitar equipamentos.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        tipo_eqp = TipoEquipamento.query.filter_by(
            id=form.tipo_equipamento.data).filter_by(ativo=True).first() 
        solicitacao = SolicitacaoEquipamento.query.filter_by(
            status = 'ABERTO').filter_by(
                turno_id = form.turno.data).filter_by(ativo=True)
            
        # Verifica se há equipamentos disponíveis para a quantidade solicitada
        # Retorna a operação caso não haja equipamentos o suficiente
        if form.qtd_preferencia.data > tipo_eqp.qtd_disponivel:
            flash('A quantidade solicitada de equipamentos excede a disponível.\
                   Por favor, insira um valor menor.', 'warning')
            return redirect(url_for('principal.inicio'))
        elif solicitacao:
            flash('Você foi colocado na lista de espera pois a sala\
                  escolhida não está disponível.', 'warning')
            status = 'SOLICITADO'
        else:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'ABERTO'

        # Insere a nova solicitação no banco de dados
        flash('A solicitação foi realizada com sucesso!.', 'success')
        solicitacao = SolicitacaoEquipamento(
                                  tipo_eqp_id=form.tipo_equipamento.data,
                                  turno_id=form.turno.data,
                                  usuario_id=current_user.id,
                                  descricao = form.descricao.data,
                                  quantidade = form.qtd_preferencia.data,
                                  data_inicio_pref=form.data_inicio_pref.data,
                                  data_fim_pref = form.data_fim_pref.data,
                                  status=status)   
        db.session.add(solicitacao)
        db.session.commit()
        return redirect(url_for('principal.inicio'))

    # Renderiza o template
    return render_template('solicitacoes/nova_solicitacao_equipamento.html', 
                           title='Nova Solicitação de Equipamento', form=form,
                           legend='Nova Solicitação de Equipamento')


@solicitacoes.route("/nova/sala", methods=['GET', 'POST'])
@login_required
@prof_required
def nova_solicitacao_sala():
    # Preenche o campo de seleção de salas
    # Retorna o usuário pra tela inicial se não houver salas cadastradas
    form = SolicitacaoSalaForm()
    
    # Recupera lista de setores do banco
    setores = Setor.query.filter_by(
        ativo=True).all()
    lista_setores = [(setor.id, setor) for setor in setores]
    
    # Recupera lista de turnos do banco
    turnos = Turno.query.filter_by(ativo=True).all()
    lista_turnos = [(turno.id, turno) for turno in turnos]
    
    # Preenche as listas de seleção
    if lista_setores and lista_turnos:
        form.setor.choices = lista_setores
        form.turno.choices = lista_turnos
    else:
        flash('Não há setores ou turnos cadastrados para solicitar salas.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        setores = Setor.query.filter_by(
            id=form.setor.data).filter_by(ativo=True).first()
        solicitacao = SolicitacaoSala.query.filter_by(turno_id = form.turno.data).filter_by(
                status = 'ABERTO').filter_by(ativo=True).first()
        
        # Verifica se a sala solicitada está disponível
        # Muda o status da solicitação de acordo com o resultado
        if setores.qtd_disponivel == 0:
            flash('Não há salas disponíveis neste setor para solicitar.', 'warning')
            return redirect(url_for('principal.inicio'))

        if setores.qtd_disponivel >= form.qtd_preferencia.data and solicitacao == None:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'ABERTO'
        else:
            flash('Você foi colocado na lista de espera pois a sala\
                  escolhida não está disponível.', 'warning')
            status = 'SOLICITADO'
            
        # Insere a nova solicitação no banco de dados
        solicitacao = SolicitacaoSala(turno_id=form.turno.data,
                                      usuario_id=current_user.id,
                                      descricao=form.descricao.data,
                                      quantidade=form.qtd_preferencia.data,
                                      setor_id=form.setor.data,
                                      data_inicio_pref=form.data_inicio_pref.data,
                                      data_fim_pref=form.data_fim_pref.data,
                                      status=status)
        db.session.add(solicitacao)
        db.session.commit()
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/nova_solicitacao_sala.html', 
                           title='Nova Solicitação de Sala', 
                           legend='Nova Solicitação de Sala', form=form)


@solicitacoes.route("/<int:solicitacao_id>/confirmar", methods=['GET', 'POST'])
@login_required
@admin_required
def confirma_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        ativo=True).filter_by(id=solicitacao_id).first_or_404()
    
    # Se a solicitação for do tipo 'Sala'...
    if solicitacao.tipo == 'SALA':
        # Em caso de envio de formulário (POST)
        form = ConfirmaSolicitacaoSalaForm()
        salas = Sala.query.filter_by(setor_id=solicitacao.setor.id).filter_by(
                status='ABERTO').filter_by(ativo=True).all()
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
            
            # Atualiza o status da sala e da solicitação
            solicitacao.setor.qtd_disponivel -= len(solicitacao.salas)
            solicitacao.status = 'CONFIRMADO'
            db.session.commit()
            envia_email_confirmacao(solicitacao)
            flash('A solicitação foi confirmada com sucesso!', 'success')
            return redirect(url_for('principal.inicio'))

        
        # Em caso de carregamento da página (GET)
        # Preenche os campos do formulário
        elif request.method == 'GET':
            form.autor.data = solicitacao.autor.nome
            form.identificacao.data = solicitacao.autor.identificacao
            form.data_abertura.data = solicitacao.data_abertura.strftime('%d/%m/%Y')
            form.turno.data = solicitacao.turno.name
            form.setor.data = solicitacao.setor.name
            form.quantidade.data = solicitacao.quantidade
            form.qtd_disponivel.data = solicitacao.setor.qtd_disponivel
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
            form.qtd_disponivel.data = solicitacao.tipo_eqp.qtd_disponivel
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
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()

    # Permite a entrega somente de solicitações confirmadas
    if solicitacao.status.name != 'CONFIRMADO':
        flash('Esta solicitação não foi confirmada!', 'warning')
        return redirect(url_for('principal.inicio'))

    # Em caso de envio de formulário (POST)
    form = EntregaSolicitacaoForm()
    if form.validate_on_submit():
        # Define a data prevista de devolução da solicitação
        # com base na data recebida no formulário
        solicitacao.data_devolucao = form.data_devolucao.data
        
        # Altera o status da sala/equipamentos associados para 'Em Uso'
        if solicitacao.tipo == 'EQUIPAMENTO':
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'EMUSO'
        if solicitacao.tipo == 'SALA':
            for sala in solicitacao.salas: 
                sala.status = 'EMUSO'

        # Atualiza o registro da solicitação
        solicitacao.status = 'EMUSO'
        solicitacao.data_entrega = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        flash('A entrega foi confirmada com sucesso!', 'success')
    else:
        flash('A data de devolução inserida é inválida.', 'warning')

    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/receber", methods=['GET', 'POST'])
@login_required
@admin_required
def recebe_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()

    # Verifica o status da solicitação para permitir seu recebimento 
    if solicitacao.status.name != 'EMUSO' and solicitacao.status != 'EMATRASO':
        flash('Esta solicitação não está em uso!', 'warning')
        return redirect(url_for('principal.inicio'))
    
    # Atualiza o status dos equipamentos recebidos para 'Disponível'
    if solicitacao.tipo == 'EQUIPAMENTO':
        for equipamento in solicitacao.equipamentos:
            equipamento.status = 'ABERTO'
        solicitacao.tipo_eqp.qtd_disponivel += len(solicitacao.equipamentos)

    # Atualiza o status da sala recebida para 'Disponível'
    # Além disso, verifica se há alguma solicitação em espera da mesma
    # sala e atualiza o status da primeira realizada, caso exista
    if solicitacao.tipo == 'SALA':
        for sala in solicitacao.salas:
            sala.status = 'ABERTO'
        solicitacao.setor.qtd_disponivel += len(solicitacao.salas)
    
    # Atualiza o registro da solicitação
    solicitacao.status = 'FECHADO'
    solicitacao.data_finalizacao = datetime.now().astimezone(fuso_horario)
    db.session.commit()
    flash('O recebimento foi confirmado com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/cancelar", methods=['POST'])
@login_required
def cancela_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()

    # Permite acesso somente ao autor da solicitação ou a um admin
    if solicitacao.autor != current_user and current_user.tipo.name != 'ADMIN':
        abort(403)

    # Verifica o status da solicitação para permitir seu cancelamento
    if (solicitacao.status.name != 'ABERTO' and solicitacao.status.name != 'SOLICITADO'
        and solicitacao.status.name != 'CONFIRMADO'):
        flash('Esta solicitação não pode ser mais cancelada!', 'warning')
        return redirect(url_for('principal.inicio'))

    # Verifica o status da solicitação no momento do cancelamento
    if solicitacao.status.name != 'ABERTO' and solicitacao.status.name != 'SOLICITADO':
        # Altera o status da sala/equipamentos associados a solicitação de volta
        # para 'Disponível' e adiciona a quantidade de equipamentos disponíveis
        if solicitacao.tipo == 'EQUIPAMENTO':
            if solicitacao.tipo_eqp:
                solicitacao.tipo_eqp.qtd_disponivel += len(solicitacao.equipamentos)
            if solicitacao.equipamentos:
                for equipamento in solicitacao.equipamentos:
                    equipamento.status = 'ABERTO'
        if solicitacao.tipo == 'SALA':
            if solicitacao.setor:
                solicitacao.setor.qtd_disponivel += len(solicitacao.salas) 
            if solicitacao.salas:
                for sala in solicitacao.salas:
                    sala.status = 'ABERTO'

    solicitacao.status = 'CANCELADO'
    solicitacao.data_cancelamento = datetime.now().astimezone(fuso_horario)
    db.session.commit()
    flash('A solicitação foi cancelada com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()

    # Impede a exclusão de solicitações indevidas
    if solicitacao.status == 'EMUSO' or solicitacao.status == 'PENDENTE':
        flash('Não é possível excluir solicitação em uso.', 'warning')
        return redirect(url_for('principal.inicio'))

    # Verifica o status da solicitação no momento da exclusão
    # Realiza um processo similar ao da função de cancelamento
    if solicitacao.status == 'CONFIRMADO':
        if solicitacao.tipo_eqp:
            solicitacao.tipo_eqp.qtd_disponivel += len(solicitacao.equipamentos)
        if solicitacao.equipamentos:
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'ABERTO'
        if solicitacao.salas:
            for sala in solicitacao.salas:
                sala.status = 'ABERTO'

    solicitacao.ativo = False
    db.session.commit()
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
        turno = Turno(name=form.nome.data, 
                      data_inicio=form.data_inicio.data, 
                      data_fim=form.data_fim.data)
        
        db.session.add(turno)
        db.session.commit()
        flash('O turno foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio'))

    return render_template('solicitacoes/novo_turno.html', 
                           title='Novo Turno',
                           legend='Novo Turno', form=form)
    