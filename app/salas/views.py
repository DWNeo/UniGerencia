from flask import (render_template, url_for, flash, abort,
                   redirect, request, Blueprint)
from flask_login import login_required

from app import db
from app.models import Sala
from app.salas.forms import SalaForm, AtualizaSalaForm
from app.usuarios.utils import admin_required

salas = Blueprint('salas', __name__)


@salas.route("/<int:sala_id>")
@login_required
@admin_required
def sala(sala_id):
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()
    return render_template('salas/sala.html', 
                           title=sala.numero, post=sala)


@salas.route("/nova", methods=['GET', 'POST'])
@login_required
@admin_required
def nova_sala():
    form = SalaForm()
    if form.validate_on_submit():
        sala = Sala(numero=form.numero.data, setor=form.setor.data, 
                    qtd_aluno=form.qtd_aluno.data)
        db.session.add(sala)
        db.session.commit()
        flash('A sala foi cadastrada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=4))
    return render_template('salas/nova_sala.html', title='Nova Sala',
                           form=form, legend='Nova Sala')


@salas.route("/<int:sala_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_sala(sala_id):
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()
    if sala.status == 'Solicitada' or sala.status == 'Em Uso' or sala.status == 'Em Atraso':
        flash('Não é possível atualizar uma sala solicitada ou em uso.', 'warning')  
        return redirect(url_for('principal.inicio', tab=4))
    form = AtualizaSalaForm()
    if form.validate_on_submit():
        sala.setor = form.setor.data
        sala.qtd_aluno = form.qtd_aluno.data
        sala.status = form.status.data
        db.session.commit()
        flash('A sala foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=4))
    elif request.method == 'GET':
        form.setor.data = sala.setor
        form.qtd_aluno.data = sala.qtd_aluno
        form.status.data = sala.status
    return render_template('salas/atualizar_sala.html', 
                           title='Atualizar Sala', form=form, 
                           legend='Atualizar Sala')


@salas.route("/<int:sala_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_sala(sala_id):
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()
    sala.ativo = False
    db.session.commit()
    flash('A Sala foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=4))