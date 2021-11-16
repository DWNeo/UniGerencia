from flask import (render_template, url_for, flash, abort,
                   redirect, request, Blueprint)
from flask_login import login_required, current_user
from app import db
from app.models import Sala
from app.salas.forms import SalaForm, AtualizaSalaForm

salas = Blueprint('salas', __name__)


@salas.route("/salas/nova", methods=['GET', 'POST'])
@login_required
def nova_sala():
    if current_user.admin == False:
        abort(403)
    form = SalaForm()
    if form.validate_on_submit():
        sala = Sala(numero=form.numero.data, 
                    setor=form.setor.data, 
                    qtd_aluno=form.qtd_aluno.data)
        db.session.add(sala)
        db.session.commit()
        flash('A sala foi cadastrada com sucesso!', 'success')
        return redirect(url_for('principal.inicio'))
    return render_template('salas/nova_sala.html', title='Nova Sala',
                           form=form, legend='Nova Sala')


@salas.route("/salas/<int:sala_id>")
@login_required
def sala(sala_id):
    if current_user.admin == False:
        abort(403)
    sala = Sala.query.get_or_404(sala_id)
    if sala.ativo == False:
        abort(404)
    return render_template('salas/sala.html', title=sala.numero, post=sala)


@salas.route("/salas/<int:sala_id>/atualizar", methods=['GET', 'POST'])
@login_required
def atualiza_sala(sala_id):
    if current_user.admin == False:
        abort(403)
    sala = Sala.query.get_or_404(sala_id)
    if sala.ativo == False:
        abort(404)
    form = AtualizaSalaForm()
    if form.validate_on_submit():
        #sala.numero = form.numero.data
        sala.setor = form.setor.data
        sala.qtd_aluno = form.qtd_aluno.data
        sala.status = form.status.data
        db.session.commit()
        flash('A sala foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', eqp_id=sala.id))
    elif request.method == 'GET':
        #form.numero.data = sala.numero
        form.setor.data = sala.setor
        form.qtd_aluno.data = sala.qtd_aluno
        form.status.data = sala.status
    return render_template('salas/atualizar_sala.html', title='Atualizar Sala',
                           form=form, legend='Atualizar Sala')


@salas.route("/salas/<int:sala_id>/excluir", methods=['POST'])
@login_required
def exclui_sala(sala_id):
    if current_user.admin == False:
        abort(403)
    sala = Sala.query.get_or_404(sala_id)
    if sala.ativo == False:
        abort(404)
    sala.ativo = False
    db.session.commit()
    flash('A Sala foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio'))
