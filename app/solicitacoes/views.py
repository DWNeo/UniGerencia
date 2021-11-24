from datetime import datetime

from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import current_user, login_required

from app import db, fuso_horario
from app.models import Solicitacao, Equipamento, Sala, TipoEquipamento
from app.solicitacoes.forms import (SolicitacaoEquipamentoForm, 
                                    SolicitacaoSalaForm,
                                    ConfirmaSolicitacaoEquipamentoForm,
                                    ConfirmaSolicitacaoSalaForm)
                                 
from app.usuarios.utils import admin_required

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/nova/equipamento", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_equipamento():
    form = SolicitacaoEquipamentoForm()
    tipos_equipamento = TipoEquipamento.query.filter_by(
        ativo=True).all()
    lista_tipos=[(tipo.id, tipo) for tipo in tipos_equipamento]
    if lista_tipos:
        form.tipo_equipamento.choices = lista_tipos
    if form.validate_on_submit():
        equipamento = Equipamento.query.filter_by(
            tipo_eqp_id=form.tipo_equipamento.data).filter_by(
            status='Disponível').filter_by(ativo=True).first()
        if equipamento == None:
            flash('Você foi colocado na lista de espera devido a falta\
                  de equipamentos disponíveis', 'warning')
            status = 'Em Espera'
        else:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'Em Aberto'
        solicitacao = Solicitacao(tipo='Equipamento',
                                  tipo_eqp_id=form.tipo_equipamento.data,
                                  turno=form.turno.data,
                                  usuario_id=current_user.id,
                                  status=status)
            
        db.session.add(solicitacao)
        db.session.commit()
        return redirect(url_for('principal.inicio'))
    return render_template('solicitacoes/nova_solicitacao_equipamento.html', 
                           title='Nova Solicitação de Equipamento', form=form,
                           legend='Nova Solicitação de Equipamento')


@solicitacoes.route("/nova/sala", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_sala():
    form = SolicitacaoSalaForm()
    salas = Sala.query.filter_by(
        ativo=True).all()
    lista_salas=[(sala.id, sala) for sala in salas]
    if lista_salas:
        form.sala.choices = lista_salas
    else:
        flash('Não há salas cadastradas para solicitar.', 'warning')
        return redirect(url_for('principal.inicio'))
    if form.validate_on_submit():
        sala = Sala.query.filter_by(
            id=form.sala.data).filter_by(ativo=True).first_or_404()
        if sala.status != 'Disponível':
            flash('Você foi colocado na lista de espera pois a sala\
                  escolhida não está disponível.', 'warning')
            status = 'Em Espera'
        else:
            flash('A solicitação foi realizada com sucesso!.', 'success')
            status = 'Em Aberto'
        solicitacao = Solicitacao(tipo='Sala', 
                                  turno=form.turno.data,
                                  usuario_id=current_user.id,
                                  sala_id=sala.id,
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

    if solicitacao.tipo == 'Sala':
        form = ConfirmaSolicitacaoSalaForm()
        if form.validate_on_submit():
            sala = Sala.query.filter_by(id=solicitacao.sala.id).filter_by(
                status='Disponível').filter_by(ativo=True).first()
            if sala == None:
                flash('A sala solicitada não stá disponível.', 'warning')
                return redirect(url_for('principal.inicio'))
            sala.status = 'Solicitada'
            solicitacao.status = 'Confirmada'
            db.session.commit()
            flash('A solicitação foi confirmada com sucesso!', 'success')
            return redirect(url_for('principal.inicio'))
        elif request.method == 'GET':
            form.autor.data = solicitacao.autor.nome
            form.identificacao.data = solicitacao.autor.identificacao
            form.data_abertura.data = solicitacao.data_abertura.strftime('%d-%m-%Y %H:%M:%S')
            form.turno.data = solicitacao.turno
            form.sala.data = solicitacao.sala
        return render_template('solicitacoes/confirmar_solicitacao_sala.html', 
                               title='Confirmar Solicitação de Sala', form=form,
                               legend='Confirmar Solicitação de Sala',
                               solicitacao=solicitacao)

    elif solicitacao.tipo == 'Equipamento':
        form = ConfirmaSolicitacaoEquipamentoForm()
        equips = Equipamento.query.filter_by(status='Disponível').filter_by(
            ativo=True).filter_by(tipo_eqp_id=solicitacao.tipo_eqp_id).all()
        lista_equips=[(equip.id, equip) for equip in equips]
        if lista_equips:
            form.equipamento.choices = lista_equips
        else:
            flash('Não há equipamentos disponíveis para solicitar.', 'warning')
            return redirect(url_for('principal.inicio'))
        if form.validate_on_submit():
            solicitacao.equipamento = Equipamento.query.filter_by(
                id=form.equipamento.data).filter_by(
                status='Disponível').filter_by(ativo=True).first()
            if solicitacao.equipamento == None:
                flash('O equipamento não está disponível.', 'warning')
                return redirect(url_for('principal.inicio'))
            solicitacao.equipamento.status = 'Solicitado'
            solicitacao.tipo_eqp.qtd_disponivel -= 1
            solicitacao.status = 'Confirmada'
            db.session.commit()
            flash('A solicitação foi confirmada com sucesso!', 'success')
            return redirect(url_for('principal.inicio'))
        elif request.method == 'GET':
            form.autor.data = solicitacao.autor.nome
            form.identificacao.data = solicitacao.autor.identificacao
            form.data_abertura.data = solicitacao.data_abertura.strftime('%d-%m-%Y %H:%M:%S')
            form.turno.data = solicitacao.turno
            form.tipo_equipamento.data = solicitacao.tipo_eqp.nome
            form.qtd_disponivel.data = solicitacao.tipo_eqp.qtd_disponivel
        return render_template('solicitacoes/confirmar_solicitacao_equipamento.html', 
                               title='Confirmar Solicitação de Equipamento', 
                               form=form, solicitacao=solicitacao,
                               legend='Confirmar Solicitação de Equipamento')

    else:
        abort(404)


@solicitacoes.route("/<int:solicitacao_id>/entregar", methods=['GET', 'POST'])
@login_required
@admin_required
def entrega_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()
    if solicitacao.status != 'Confirmada':
        flash('Esta solicitação não foi confirmada!', 'warning')
        return redirect(url_for('principal.inicio'))
    data_atual = datetime.now().astimezone(fuso_horario).strftime('%Y-%m-%d')
    if solicitacao.turno == 'Matutino':
        string_data = (data_atual + ' 12:30:00')
        solicitacao.data_devolucao = datetime.strptime(
            string_data, '%Y-%m-%d %H:%M:%S')
    if solicitacao.turno == 'Noturno' or solicitacao.turno == 'Integral':
        string_data = (data_atual + ' 22:30:00')
        solicitacao.data_devolucao = datetime.strptime(
            string_data, '%Y-%m-%d %H:%M:%S')
    solicitacao.status = 'Em Uso'
    if solicitacao.equipamento:
        solicitacao.equipamento.status = 'Em Uso'
    if solicitacao.sala:
        solicitacao.sala.status = 'Em Uso'
    solicitacao.data_entrega = datetime.now().astimezone(fuso_horario)
    db.session.commit()
    flash('A entrega foi confirmada com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))


@solicitacoes.route("/<int:solicitacao_id>/receber", methods=['GET', 'POST'])
@login_required
@admin_required
def recebe_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()
    if solicitacao.status != 'Em Uso' and solicitacao.status != 'Em Atraso':
        flash('Esta solicitação não está em uso!', 'warning')
        return redirect(url_for('principal.inicio'))
    if solicitacao.equipamento:
        solicitacao_espera = Solicitacao.query.filter_by(
            status='Em Espera').filter_by(
            tipo_eqp_id=solicitacao.tipo_eqp.id).filter_by(
            ativo=True).order_by(Solicitacao.id.asc()).first()
        solicitacao.equipamento.status = 'Disponível'
        solicitacao.tipo_eqp.qtd_disponivel += 1
    if solicitacao.sala:
        solicitacao_espera = Solicitacao.query.filter_by(
            status='Em Espera').filter_by(
            sala_id=solicitacao.sala.id).filter_by(
            ativo=True).order_by(Solicitacao.id.asc()).first()
        solicitacao.sala.status = 'Disponível'
    if solicitacao_espera:
        solicitacao_espera.status = 'Em Aberto'
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
    if solicitacao.autor != current_user and current_user.admin == False:
        abort(403)
    if solicitacao.status != 'Em Aberto' and solicitacao.status != 'Confirmada':
        flash('Esta solicitação não pode ser mais cancelada!', 'warning')
        return redirect(url_for('principal.inicio'))
    if solicitacao.status != 'Em Aberto':
        if solicitacao.tipo_eqp:
            solicitacao.tipo_eqp.qtd_disponivel += 1
        if solicitacao.equipamento:
            if solicitacao.equipamento.status != 'Disponível':
                solicitacao.equipamento.status = 'Disponível'
        if solicitacao.sala: 
            if solicitacao.sala.status != 'Disponível':
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
    if solicitacao.status != 'Em Aberto' and solicitacao.status != 'Cancelada' and solicitacao.status != 'Finalizada':
        if solicitacao.tipo_eqp:
            solicitacao.tipo_eqp.qtd_disponivel += 1
        if solicitacao.equipamento:
            if solicitacao.equipamento.status != 'Disponível':
                solicitacao.equipamento.status = 'Disponível'
        if solicitacao.sala: 
            if solicitacao.sala.status != 'Disponível':
                solicitacao.sala.status = 'Disponível'
    solicitacao.ativo = False
    db.session.commit()
    flash('A solicitação foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))