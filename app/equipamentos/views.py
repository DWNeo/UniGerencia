from flask import (render_template, url_for, flash, abort,
                   redirect, request, Blueprint)
from flask_login import login_required

from app import db
from app.models import Equipamento, TipoEquipamento
from app.equipamentos.forms import (EquipamentoForm, AtualizaEquipamentoForm,
                                    TipoEquipamentoForm)
from app.usuarios.utils import admin_required

equipamentos = Blueprint('equipamentos', __name__)


@equipamentos.route("/<int:eqp_id>")
@login_required
@admin_required
def equipamento(eqp_id):
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()
    return render_template('equipamentos/equipamento.html', 
                           title=equipamento.patrimonio, 
                           post=equipamento)


@equipamentos.route("/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_equipamento():
    form = EquipamentoForm()
    tipos_eqp = TipoEquipamento.query.filter_by(
        ativo=True).all()
    lista_tipos=[(tipo.id, tipo.nome) for tipo in tipos_eqp]
    if lista_tipos:
        form.tipo_eqp.choices = lista_tipos
    else:
        flash('Não há tipos de equipamento cadastrados.', 'warning')
        return redirect(url_for('principal.inicio', tab=3))
    if form.validate_on_submit():
        tipo_eqp = TipoEquipamento.query.filter_by(
            id=form.tipo_eqp.data).filter_by(ativo=True).first()
        tipo_eqp.qtd_disponivel += 1
        equipamento = Equipamento(patrimonio=form.patrimonio.data, 
                                  descricao=form.descricao.data, 
                                  tipo_eqp_id=form.tipo_eqp.data)
        db.session.add(equipamento)
        db.session.commit()
        flash('O equipamento foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=3))
    return render_template('equipamentos/novo_equipamento.html', 
                           title='Novo Equipamento',
                           legend='Novo Equipamento', form=form)


@equipamentos.route("/novo_tipo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_tipo_equipamento():
    form = TipoEquipamentoForm()
    if form.validate_on_submit():
        tipo_eqp = TipoEquipamento(nome=form.nome.data)
        db.session.add(tipo_eqp)
        db.session.commit()
        flash('O tipo de equipamento foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=3))
    return render_template('equipamentos/novo_tipo_equipamento.html', 
                           title='Novo Tipo de Equipamento',
                           legend='Novo Tipo de Equipamento', form=form)


@equipamentos.route("/<int:eqp_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_equipamento(eqp_id):
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()
    if equipamento.status == 'Solicitado' or equipamento.status == 'Em Uso' or equipamento.status == 'Em Atraso':
        flash('Não é possível atualizar um equipamento solicitado ou em uso.', 'warning')  
        return redirect(url_for('principal.inicio', tab=3))
    form = AtualizaEquipamentoForm()
    if form.validate_on_submit():
        if equipamento.status != 'Disponível':
            if form.status.data == 'Disponível':
                equipamento.tipo_eqp.qtd_disponivel += 1
        elif equipamento.status == 'Disponível':
            if form.status.data != 'Disponível':
                equipamento.tipo_eqp.qtd_disponivel -= 1
        equipamento.descricao = form.descricao.data
        equipamento.status = form.status.data
        db.session.commit()
        flash('O equipamento foi atualizado com sucesso!', 'success')  
        return redirect(url_for('principal.inicio', tab=3))
    elif request.method == 'GET':
        form.descricao.data = equipamento.descricao
        form.status.data = equipamento.status
    return render_template('equipamentos/atualizar_equipamento.html', 
                           title='Atualizar Equipamento',
                           legend='Atualizar Equipamento',
                           form=form)


@equipamentos.route("/<int:eqp_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_equipamento(eqp_id):
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()
    equipamento.ativo = False
    if equipamento.status == 'Disponível':
        tipo_eqp = TipoEquipamento.query.filter_by(
            id=equipamento.tipo_eqp_id).filter_by(ativo=True).first()
        tipo_eqp.qtd_disponivel -= 1
    db.session.commit()
    flash('O equipamento foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=3))