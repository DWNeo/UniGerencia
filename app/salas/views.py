from datetime import datetime

from flask import (render_template, url_for, flash, abort,
                   redirect, request, Blueprint)
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import RelatorioSala, Sala, Relatorio, Solicitacao, Setor, SolicitacaoSala
from app.salas.forms import (SalaForm, AtualizaSalaForm, IndisponibilizaSalaForm,
                             RelatorioSalaForm, AtualizaRelatorioSalaForm, SetorForm)
from app.usuarios.utils import prof_required, admin_required

salas = Blueprint('salas', __name__)


@salas.route("/<int:sala_id>")
@login_required
@prof_required
def sala(sala_id):
    # Recupera a sala pela ID
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()

    # Recupera as últimas solicitações associadas a sala
    solicitacoes = Solicitacao.query.filter(
        SolicitacaoSala.salas.contains(sala)).filter_by(ativo=True).order_by(
        SolicitacaoSala.id.desc()).limit(5)

    # Renderiza o template
    return render_template('salas/sala.html', 
                           title=sala, sala=sala,
                           solicitacoes=solicitacoes)

@salas.route("/novo_setor", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_setor():
    # Valida os dados do formulário enviado e insere um 
    # novo registro de sala no banco de dados
    form = SetorForm()
    if form.validate_on_submit():
        setor = Setor(name=form.nome.data)
        db.session.add(setor)
        db.session.commit()
        flash('O Setor foi cadastrado com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=4))

    return render_template('salas/novo_setor.html', title='Novo Setor',
                           form=form, legend='Novo Setor')


@salas.route("/nova", methods=['GET', 'POST'])
@login_required
@admin_required
def nova_sala():
    # Valida os dados do formulário enviado e insere um 
    # novo registro de sala no banco de dados
    form = SalaForm()
    setores = Setor.query.filter_by(ativo=True).all()

    lista_setores = [(setor.id, setor) for setor in setores]
    if lista_setores:
        form.setor.choices = lista_setores
    else:
        flash('Não há setores cadastrados para cadastrar a sala.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        setor = Setor.query.filter_by(id=
                form.setor.data).filter_by(ativo=True).first_or_404()
        setor.qtd_disponivel += 1
        sala = Sala(numero=form.numero.data, setor_id=setor.id, 
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
    # Recupera a sala pela ID e retorna erro 404 caso não encontre
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()
    
    # Valida o formulário enviado e atualiza o registro
    # da sala no banco de dados de acordo com ele
    form = AtualizaSalaForm()
    setores = Setor.query.filter_by(ativo=True).all()
    lista_setores = [(setor.id, setor.name) for setor in setores]

    form.setor.choices = lista_setores

    if form.validate_on_submit():
        setor = Setor.query.filter_by(id=form.setor.data).filter_by(ativo=True).first_or_404()

        sala.setor_id = setor.id
        sala.qtd_aluno = form.qtd_aluno.data
        sala.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        flash('A sala foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=4))
    elif request.method == 'GET':
        form.qtd_aluno.data = sala.qtd_aluno

    return render_template('salas/atualizar_sala.html', 
                           title='Atualizar Sala', form=form, 
                           legend='Atualizar Sala')


@salas.route("/<int:sala_id>/disponibilizar", methods=['GET', 'POST'])
@login_required
@admin_required
def disponibiliza_sala(sala_id):
    # Valida os dados do formulário enviado e altera o status
    # do equipamento escolhido para 'Disponível'
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()
    
    # Verifica se o equipamento está indisponível
    if sala.status.name != 'DESABILITADO' and sala.status.name != 'EMMANUTENCAO':
        flash('Essa sala já está disponível.', 'warning')
        return redirect(url_for('principal.inicio', tab=4))

    # Altera o registro do equipamento
    sala.motivo_indisponibilidade = None
    sala.status = 'ABERTO'
    sala.data_atualizacao = datetime.now().astimezone(fuso_horario)

    db.session.commit()
    flash('A sala foi disponibilizada com sucesso!', 'success') 
    return redirect(url_for('principal.inicio', tab=4))


@salas.route("/<int:sala_id>/indisponibilizar", methods=['GET', 'POST'])
@login_required
@admin_required
def indisponibiliza_sala(sala_id):
    # Valida os dados do formulário enviado e altera o status
    # da sala escolhida para 'Indisponível'
    form = IndisponibilizaSalaForm()
    if form.validate_on_submit():
        sala = Sala.query.filter_by(
            id=sala_id).filter_by(ativo=True).first_or_404()
        
        # Verifica se a sala está disponível
        if sala.status != 'ABERTA':
            flash('Você não pode tornar essa sala indisponível.', 'warning')
            return redirect(url_for('principal.inicio', tab=4))

        # Altera o registro do equipamento
        sala.motivo_indisponibilidade = form.motivo.data
        sala.status = 'DESABILITADO'
        sala.data_atualizacao = datetime.now().astimezone(fuso_horario)

        db.session.commit()
        flash('A sala foi indisponibilizada com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=4))

    return render_template('salas/indisponibilizar_sala.html', 
                           title='Indisponibilizar Sala',
                           legend='Indisponibilizar Sala', form=form)


@salas.route("/<int:sala_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_sala(sala_id):
    # Recupera a sala pela ID
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()

    # Impede uma sala de ser indevidamente excluída
    if sala.status != 'ABERTO' and sala.status != 'DESABILITADO':
        flash('Não é possível excluir uma sala solicitada ou em uso.', 'warning')
        return redirect(url_for('principal.inicio', tab=4))

    if Setor.status.name == 'ABERTO':
        setor = Setor.query.filter_by(
            id=sala.setor_id).filter_by(ativo=True).first()
        setor.qtd_disponivel -= 1

    # Desativa o registro da sala
    sala.ativo = False
    db.session.commit()
    flash('A Sala foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=4))


@salas.route("/<int:sala_id>/relatorios", methods=['GET', 'POST'])
@login_required
@admin_required
def relatorios(sala_id):
    # Recupera os relatórios do equipamento pela ID
    sala = Sala.query.filter_by(
        id=sala_id).filter_by(ativo=True).first_or_404()
    relatorios = RelatorioSala.query.filter_by(
        sala_id=sala.id).filter_by(ativo=True).all()

    return render_template('salas/relatorios.html', 
                           title='Relatórios da Sala',
                           legend='Relatórios da Sala',
                           relatorios=relatorios, sala_id=sala_id)


@salas.route("/<int:sala_id>/relatorios/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_relatorio(sala_id):
    # Valida o formulário e insere o novo relatório no banco de dados
    form = RelatorioSalaForm()
    if form.validate_on_submit():
        status = 'ABERTO'
        relatorio = RelatorioSala(tipo_relatorio=form.tipo.data, 
                              conteudo=form.conteudo.data,
                              manutencao=form.manutencao.data,
                              reforma=form.reforma.data,
                              detalhes=form.detalhes.data,
                              status = status,
                              usuario_id=current_user.id,
                              sala_id=sala_id)
        db.session.add(relatorio)
        db.session.commit()
        flash('O relatório foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('salas.relatorios', sala_id=sala_id))

    return render_template('salas/novo_relatorio.html', 
                           title='Novo Relatório', sala_id=sala_id,
                           legend='Novo Relatório', form=form)


@salas.route("/<int:sala_id>/relatorios/<int:id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_relatorio(sala_id, id):
    # Recupera o relatório pela ID
    relatorio = Relatorio.query.filter_by(
        id=id).filter_by(ativo=True).first_or_404()
    # Valida o formulário e atualiza o relatório no banco de dados
    form = AtualizaRelatorioSalaForm()

    # Impede relatórios finalizados de serem atualizados
    if relatorio.status.name == 'FECHADO':
        flash('Este relatório já foi finalizado.', 'success') 
        return redirect(url_for('salas.relatorios', sala_id=sala_id))

    if form.validate_on_submit():
        relatorio.conteudo = form.conteudo.data
        relatorio.detalhes = form.detalhes.data
       

        # Atualiza as datas dependendo do status selecionado
        # Status 'Finalizado' -> Data de Finalização
        # Status 'Aberto' -> Data de Atualização
        if form.status.data == True:
            relatorio.status = 'FECHADO'
            relatorio.data_finalizacao = datetime.now().astimezone(fuso_horario)
        else:
            relatorio.data_atualizacao = datetime.now().astimezone(fuso_horario)

        # Atualiza o relatório
        db.session.commit()
        flash('O relatório foi atualizado com sucesso!', 'success') 
        return redirect(url_for('salas.relatorios', sala_id=sala_id))
    elif request.method == 'GET':
        form.tipo.data = relatorio.tipo_relatorio.value
        form.conteudo.data = relatorio.conteudo
        form.manutencao.data = relatorio.manutencao
        form.reforma.data = relatorio.reforma
        form.detalhes.data = relatorio.detalhes
        form.status.data = False

    return render_template('salas/atualizar_relatorio.html', 
                           title='Atualizar Relatório', sala_id=sala_id,
                           legend='Atualizar Relatório', form=form)