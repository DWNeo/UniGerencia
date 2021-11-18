from flask import (render_template, url_for, flash, abort,
                   redirect, request, Blueprint)
from flask_login import login_required

from app import db
from app.models import Equipamento
from app.equipamentos.forms import EquipamentoForm, AtualizaEquipamentoForm
from app.usuarios.utils import admin_required

equipamentos = Blueprint('equipamentos', __name__)


@equipamentos.route("/<int:eqp_id>")
@login_required
@admin_required
def equipamento(eqp_id):
    equipamento = Equipamento.query.get_or_404(eqp_id)
    if equipamento.ativo == False:
        abort(404)
    return render_template('equipamentos/equipamento.html', 
                           title=equipamento.patrimonio, 
                           post=equipamento)


@equipamentos.route("/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_equipamento():
    form = EquipamentoForm()
    if form.validate_on_submit():
        equipamento = Equipamento(patrimonio=form.patrimonio.data, 
                                  descricao=form.descricao.data, 
                                  tipo_eqp=form.tipo_eqp.data)
        db.session.add(equipamento)
        db.session.commit()
        flash('O equipamento foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio'))
    return render_template('equipamentos/novo_equipamento.html', 
                           title='Novo Equipamento',
                           legend='Novo Equipamento', form=form)


@equipamentos.route("/<int:eqp_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_equipamento(eqp_id):
    equipamento = Equipamento.query.get_or_404(eqp_id)
    if equipamento.ativo == False:
        abort(404)
    form = AtualizaEquipamentoForm()
    if form.validate_on_submit():
        equipamento.descricao = form.descricao.data
        equipamento.tipo_eqp = form.tipo_eqp.data
        equipamento.status = form.status.data
        db.session.commit()
        flash('O equipamento foi atualizado com sucesso!', 'success')  
        return redirect(url_for('principal.inicio'))
    elif request.method == 'GET':
        form.descricao.data = equipamento.descricao
        form.tipo_eqp.data = equipamento.tipo_eqp
        form.status.data = equipamento.status
    return render_template('equipamentos/atualizar_equipamento.html', 
                           title='Atualizar Equipamento',
                           legend='Atualizar Equipamento',
                           form=form)


@equipamentos.route("/<int:eqp_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_equipamento(eqp_id):
    equipamento = Equipamento.query.get_or_404(eqp_id)
    if equipamento.ativo == False:
        abort(404)
    equipamento.ativo = False
    db.session.commit()
    flash('O equipamento foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))