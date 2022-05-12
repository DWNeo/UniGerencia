from datetime import datetime 
import pandas as pd

from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import current_user, login_required

from app import db, fuso_horario
from app.models import Solicitacao, Equipamento, Sala, TipoEquipamento, Turno
from app.solicitacoes.forms import (SolicitacaoEquipamentoForm, TurnoForm,
                                    SolicitacaoSalaForm, EntregaSolicitacaoForm,
                                    ConfirmaSolicitacaoEquipamentoForm,
                                    ConfirmaSolicitacaoSalaForm)
                                 
from app.usuarios.utils import admin_required

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/<int:solicitacao_id>")
@login_required
def solicitacao(solicitacao_id):
    # Recupera a sala pela ID
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()

    # Permite acesso somente ao autor da solicitação ou a um admin
    if solicitacao.autor != current_user and current_user.admin == False:
        abort(403)

    # Renderiza o template
    return render_template('solicitacoes/solicitacao.html', 
                           title=solicitacao, solicitacao=solicitacao)


@solicitacoes.route("/nova/equipamento", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_equipamento():
    # Preenche o campo de seleção de tipos de equipamento
    form = SolicitacaoEquipamentoForm()
    tipos_equipamento = TipoEquipamento.query.filter_by(
        ativo=True).all()
    lista_tipos=[(tipo.id, tipo) for tipo in tipos_equipamento]
    if lista_tipos:
        form.tipo_equipamento.choices = lista_tipos

    if form.validate_on_submit():
        tipo_eqp = TipoEquipamento.query.filter_by(
            id=form.tipo_equipamento.data).filter_by(ativo=True).first() 

        # Verifica se há equipamentos disponíveis para a quantidade solicitada
        # Retona a operação caso não haja equipamentos o suficiente
        if form.qtd_equipamento.data > tipo_eqp.qtd_disponivel:
            flash('A quantidade solicitada de equipamentos excede a disponível.\
                   Por favor, insira um valor menor.', 'warning')
            return redirect(url_for('principal.inicio'))

        # Insere a nova solicitação no banco de dados
        flash('A solicitação foi realizada com sucesso!.', 'success')
        solicitacao = Solicitacao(tipo='Equipamento',
                                  tipo_eqp_id=form.tipo_equipamento.data,
                                  turno=form.turno.data,
                                  qtd_equipamento=form.qtd_equipamento.data,
                                  usuario_id=current_user.id,
                                  data_preferencial=form.data_preferencial.data)   
        db.session.add(solicitacao)
        db.session.commit()
        return redirect(url_for('principal.inicio'))

    # Renderiza o template
    return render_template('solicitacoes/nova_solicitacao_equipamento.html', 
                           title='Nova Solicitação de Equipamento', form=form,
                           legend='Nova Solicitação de Equipamento')


@solicitacoes.route("/nova/sala", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_sala():
    # Preenche o campo de seleção de salas
    # Retorna o usuário pra tela inicial se não houver salas cadastradas
    form = SolicitacaoSalaForm()
    salas = Sala.query.filter_by(
        ativo=True).all()
    lista_salas = [(sala.id, sala) for sala in salas]
    if lista_salas:
        form.sala.choices = lista_salas
    else:
        flash('Não há salas cadastradas para solicitar.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        sala = Sala.query.filter_by(
            id=form.sala.data).filter_by(ativo=True).first_or_404()

        # Verifica se a sala solicitada está disponível
        # Muda o status da solicitação de acordo com o resultado
        if sala.status != 'Disponível':
            flash('Você foi colocado na lista de espera pois a sala\
                  escolhida não está disponível.', 'warning')
            status = 'Em Espera'
        else:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'Em Aberto'

        # Insere a nova solicitação no banco de dados
        solicitacao = Solicitacao(tipo='Sala', 
                                  turno=form.turno.data,
                                  usuario_id=current_user.id,
                                  sala_id=sala.id,
                                  data_preferencial=form.data_preferencial.data,
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
    if solicitacao.tipo == 'Sala':
        # Em caso de envio de formulário (POST)
        form = ConfirmaSolicitacaoSalaForm()
        if form.validate_on_submit():
            # Realiza uma última verificação de disponibilidade da sala
            # Cancela a operação caso a sala não esteja mais disponível
            sala = Sala.query.filter_by(id=solicitacao.sala.id).filter_by(
                status='Disponível').filter_by(ativo=True).first()
            if sala == None:
                flash('A sala solicitada não está disponível.', 'warning')
                return redirect(url_for('principal.inicio'))

            # Atualiza o status da sala e da solicitação
            sala.status = 'Solicitada'
            solicitacao.status = 'Confirmada'
            db.session.commit()
            flash('A solicitação foi confirmada com sucesso!', 'success')
            return redirect(url_for('principal.inicio'))
        # Em caso de carregamento da página (GET)
        # Preenche os campos do formulário
        elif request.method == 'GET':
            print(solicitacao.data_preferencial)
            form.autor.data = solicitacao.autor.nome
            form.identificacao.data = solicitacao.autor.identificacao
            form.data_abertura.data = solicitacao.data_abertura.strftime('%d/%m/%Y %H:%M:%S')
            form.turno.data = solicitacao.turno
            form.sala_solicitada.data = solicitacao.sala
            form.data_preferencial.data = solicitacao.data_preferencial.strftime('%d/%m/%Y %H:%M:%S')

        return render_template('solicitacoes/confirmar_solicitacao_sala.html', 
                               title='Confirmar Solicitação de Sala', form=form,
                               legend='Confirmar Solicitação de Sala',
                               solicitacao=solicitacao)
    
    # Se a solicitação for do tipo 'Equipamento'...
    elif solicitacao.tipo == 'Equipamento':
        # Preenche o campo de seleção de equipamentos disponíveis
        # Retorna o usuário pra tela inicial se não houver nenhum
        form = ConfirmaSolicitacaoEquipamentoForm()
        equips = Equipamento.query.filter_by(status='Disponível').filter_by(
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
                    status='Disponível').filter_by(ativo=True).first()
                if equipamento == None:
                    flash('Um equipamento não está mais disponível.', 'warning')
                    return redirect(url_for('principal.inicio'))
                # Adiciona cada equipamento verificado pra uma lista
                lista_equips.append(equipamento)

            # Associa os equipamentos da lista à solicitação
            solicitacao.equipamentos = lista_equips

            # Verifica se a quantidade de equipamentos selecionados pelo
            # admin é igual a quantidade solicitada
            if len(solicitacao.equipamentos) != solicitacao.qtd_equipamento:
                flash('A quantidade de equipamentos selecionados\
                       é diferente da solicitada.', 'warning')
                return redirect(url_for('principal.inicio'))

            # Associa os equipamentos à solicitação e
            # atualiza o status desses equipamentos
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'Solicitado'

            # Atualiza a quantidade de equipamentos disponíveis
            solicitacao.tipo_eqp.qtd_disponivel -= len(solicitacao.equipamentos)
            solicitacao.status = 'Confirmada'
            db.session.commit()
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
            form.qtd_solicitada.data = solicitacao.qtd_equipamento
            form.qtd_disponivel.data = solicitacao.tipo_eqp.qtd_disponivel
            form.equipamentos.data = solicitacao.equipamentos
            form.data_preferencial.data = solicitacao.data_preferencial.strftime('%d/%m/%Y %H:%M:%S')

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
    if solicitacao.status != 'Confirmada':
        flash('Esta solicitação não foi confirmada!', 'warning')
        return redirect(url_for('principal.inicio'))

    # Em caso de envio de formulário (POST)
    form = EntregaSolicitacaoForm()
    if form.validate_on_submit():
        # Define a data prevista de devolução da solicitação
        # com base na data recebida no formulário
        solicitacao.data_devolucao = form.data_devolucao.data
        
        # Altera o status da sala/equipamentos associados para 'Em Uso'
        if solicitacao.equipamentos:
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'Em Uso'
        if solicitacao.sala: 
            solicitacao.sala.status = 'Em Uso'

        # Atualiza o registro da solicitação
        solicitacao.status = 'Em Uso'
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
    if solicitacao.status != 'Em Uso' and solicitacao.status != 'Em Atraso':
        flash('Esta solicitação não está em uso!', 'warning')
        return redirect(url_for('principal.inicio'))
    
    # Atualiza o status dos equipamentos recebidos para 'Disponível'
    if solicitacao.equipamentos:
        for equipamento in solicitacao.equipamentos:
            equipamento.status = 'Disponível'
        solicitacao.tipo_eqp.qtd_disponivel += len(solicitacao.equipamentos)

    # Atualiza o status da sala recebida para 'Disponível'
    # Além disso, verifica se há alguma solicitação em espera da mesma
    # sala e atualiza o status da primeira realizada, caso exista
    if solicitacao.sala:
        solicitacao.sala.status = 'Disponível'
        solicitacao_espera = Solicitacao.query.filter_by(
            status='Em Espera').filter_by(
            sala_id=solicitacao.sala.id).filter_by(
            ativo=True).order_by(Solicitacao.id.asc()).first()
        if solicitacao_espera:
            solicitacao_espera.status = 'Em Aberto'
    
    # Atualiza o registro da solicitação
    solicitacao.status = 'Finalizada'
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
    if solicitacao.autor != current_user and current_user.admin == False:
        abort(403)

    # Verifica o status da solicitação para permitir seu cancelamento
    if (solicitacao.status != 'Em Aberto' and solicitacao.status != 'Em Espera'
        and solicitacao.status != 'Confirmada'):
        flash('Esta solicitação não pode ser mais cancelada!', 'warning')
        return redirect(url_for('principal.inicio'))

    # Verifica o status da solicitação no momento do cancelamento
    if solicitacao.status != 'Em Aberto' and solicitacao.status != 'Em Espera':
        # Altera o status da sala/equipamentos associados a solicitação de volta
        # para 'Disponível' e adiciona a quantidade de equipamentos disponíveis
        if solicitacao.tipo_eqp:
            solicitacao.tipo_eqp.qtd_disponivel += len(solicitacao.equipamentos)
        if solicitacao.equipamentos:
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'Disponível'
        if solicitacao.sala: 
            solicitacao.sala.status = 'Disponível'

    solicitacao.status = 'Cancelada'
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
    if solicitacao.status == 'Em Uso' or solicitacao.status == 'Em Atraso':
        flash('Não é possível excluir solicitação em uso.', 'warning')
        return redirect(url_for('principal.inicio'))

    # Verifica o status da solicitação no momento da exclusão
    # Realiza um processo similar ao da função de cancelamento
    if solicitacao.status == 'Confirmada':
        if solicitacao.tipo_eqp:
            solicitacao.tipo_eqp.qtd_disponivel += len(solicitacao.equipamentos)
        if solicitacao.equipamentos:
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'Disponível'
        if solicitacao.sala: 
            solicitacao.sala.status = 'Disponível'

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
        nome = form.nome.data
        data_inicio = datetime.timestamp(form.hora_inicio.data) 
        data_fim =  datetime.timestamp(form.hora_fim.data) 
        turno = Turno(nome,data_inicio,data_fim)
        
        db.session.add(turno)
        db.session.commit()
        flash('O turno foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=3))

    return render_template('solicitacoes/novo_turno.html', 
                           title='Novo Turno',
                           legend='Novo Turno', form=form)