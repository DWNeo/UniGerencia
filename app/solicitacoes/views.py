from flask import (render_template, url_for, flash, 
                   redirect, abort, request, Blueprint)
from flask_login import current_user, login_required

from app import db
from app.models import Solicitacao, Equipamento, Sala
from app.solicitacoes.forms import (SolicitacaoEquipamentoForm, 
                                    AtualizaSolicitacaoEquipamentoForm,
                                    SolicitacaoSalaForm,
                                    AtualizaSolicitacaoSalaForm)
                                 
from app.usuarios.utils import admin_required

solicitacoes = Blueprint('solicitacoes', __name__)


@solicitacoes.route("/nova/equipamento", methods=['GET', 'POST'])
@login_required
def nova_solicitacao_equipamento():
    form = SolicitacaoEquipamentoForm()
    if form.validate_on_submit():
        equipamento = Equipamento.query.filter_by(
            tipo_eqp=form.tipo_equipamento.data).filter_by(
            status='Disponível').filter_by(ativo=True).first()
        if equipamento == None:
            flash('Não há equipamentos do tipo escolhido\
                  disponíveis para solicitar.', 'warning')
        else:
            solicitacao = Solicitacao(tipo='Equipamento',
                                      tipo_equipamento=form.tipo_equipamento.data,
                                      turno=form.turno.data,
                                      usuario_id=current_user.id,
                                      status='Em Aberto')
            flash('A solicitação foi realizada com sucesso!.', 'success')
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
        ativo=True).filter_by(status='Disponível').all()
    lista_salas=[(sala.numero, sala.numero) for sala in salas]
    if lista_salas:
        form.sala.choices = lista_salas
    else:
        flash('Não há salas disponíveis para solicitar.', 'warning')
        return redirect(url_for('principal.inicio'))
    if form.validate_on_submit():
        sala = Sala.query.filter_by(
            numero=form.sala.data).filter_by(ativo=True).first_or_404()
        sala.status = 'Solicitada'
        solicitacao = Solicitacao(tipo='Sala', 
                                  turno=form.turno.data,
                                  usuario_id=current_user.id,
                                  sala_id=sala.id,
                                  status='Em Aberto')
        db.session.add(solicitacao)
        db.session.commit()
        flash('A solicitação foi realizada com sucesso!.', 'success')
        return redirect(url_for('principal.inicio'))
    return render_template('solicitacoes/nova_solicitacao_sala.html', 
                           title='Nova Solicitação de Sala', 
                           legend='Nova Solicitação de Sala', form=form)


@solicitacoes.route("/<int:solicitacao_id>/sala/confirmar", methods=['GET', 'POST'])
@login_required
@admin_required
def confirma_solicitacao_sala(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        ativo=True).filter_by(id=solicitacao_id).first_or_404()
    form = AtualizaSolicitacaoSalaForm()
    if form.validate_on_submit():
        solicitacao.status = 'Confirmada'
        db.session.commit()
        flash('A solicitação foi confirmada com sucesso!', 'success')
        return redirect(url_for('principal.inicio'))
    elif request.method == 'GET':
        form.autor.data = solicitacao.autor.nome
        form.identificacao.data = solicitacao.autor.identificacao
        form.data_abertura.data = solicitacao.data_abertura.strftime('%d-%m-%Y %H:%M:%S')
        form.turno.data = solicitacao.turno
        form.sala.data = solicitacao.sala.numero
        print(solicitacao.sala.numero)
    return render_template('solicitacoes/confirmar_solicitacao_sala.html', 
                           title='Confirmar Solicitação de Sala', form=form,
                           legend='Confirmar Solicitação de Sala')


@solicitacoes.route("/<int:solicitacao_id>/excluir", methods=['POST'])
@login_required
def exclui_solicitacao(solicitacao_id):
    solicitacao = Solicitacao.query.filter_by(
        id=solicitacao_id).filter_by(ativo=True).first_or_404()
    if solicitacao.autor != current_user and current_user.admin == False:
        abort(403)
    solicitacao.ativo = False
    if solicitacao.equipamento:
        solicitacao.equipamento.status = 'Disponível'
    if solicitacao.sala: 
        solicitacao.sala.status = 'Disponível'
    db.session.commit()
    flash('A solicitação foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))