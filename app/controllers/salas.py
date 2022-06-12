from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_required

from app.models import (RelatorioSala, Sala, Solicitacao, Setor,
                        prof_required, admin_required)
from app.forms.salas import (SalaForm, AtualizaSalaForm, IndisponibilizaSalaForm,
                             RelatorioSalaForm, AtualizaRelatorioSalaForm, SetorForm)

salas = Blueprint('salas', __name__)


@salas.route("/<int:sala_id>")
@login_required
@prof_required
def sala(sala_id):
    # Recupera as últimas solicitações associadas a sala
    sala = Sala.recuperar_id(sala_id)
    solicitacoes = Solicitacao.recuperar_ultimas_sala(sala, 3)
    return render_template('salas/sala.html', 
                           title=sala, sala=sala,
                           solicitacoes=solicitacoes)

@salas.route("/novo_setor", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_setor():
    # Valida os dados do formulário enviado e insere um 
    # novo registro de setor no banco de dados
    form = SetorForm()
    if form.validate_on_submit():
        setor = Setor.criar(form)
        setor.inserir()
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
    setores = Setor.recuperar_tudo()

    # Preenche o seletor de setor para a sala
    lista_setores = [(setor.id, setor) for setor in setores]
    if lista_setores:
        form.setor.choices = lista_setores
    else:
        flash('Não há setores cadastrados para cadastrar a sala.', 'warning')
        return redirect(url_for('principal.inicio'))

    if form.validate_on_submit():
        sala = Sala.criar(form)
        sala.inserir()
        flash('A sala foi cadastrada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=4))

    return render_template('salas/nova_sala.html', title='Nova Sala',
                           form=form, legend='Nova Sala')


@salas.route("/<int:sala_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_sala(sala_id):
    # Valida o formulário enviado e atualiza o registro
    # da sala no banco de dados de acordo com ele
    sala = Sala.recuperar_id(sala_id)
    form = AtualizaSalaForm()
    
    # Preenche o seletor de setores
    setores = Setor.recuperar_tudo()
    lista_setores = [(setor.id, setor.name) for setor in setores]
    form.setor.choices = lista_setores

    if form.validate_on_submit():
        sala.atualizar(form)
        flash('A sala foi atualizada com sucesso!', 'success')
        return redirect(url_for('principal.inicio', tab=4))
    elif request.method == 'GET':
        form.qtd_aluno.data = sala.qtd_aluno
        form.setor.data = sala.setor_id

    return render_template('salas/atualizar_sala.html', 
                           title='Atualizar Sala', form=form, 
                           legend='Atualizar Sala')


@salas.route("/<int:sala_id>/disponibilizar", methods=['GET', 'POST'])
@login_required
@admin_required
def disponibiliza_sala(sala_id):
    # Valida os dados do formulário enviado e altera o status
    # do equipamento escolhido para 'Disponível'
    sala = Sala.recuperar_id(sala_id)
    if sala.verificar_disponibilidade():
        flash('Essa sala já está disponível.', 'warning')
        return redirect(url_for('principal.inicio', tab=4))

    # Altera o registro do equipamento
    sala.disponibilizar()
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
        # Verifica se a sala está disponível
        sala = Sala.recuperar_id(sala_id)
        if not sala.verificar_disponibilidade():
            flash('Você não pode tornar essa sala indisponível.', 'warning')
            return redirect(url_for('principal.inicio', tab=4))
        
        # Altera o registro do equipamento
        sala.indisponibilizar(form)
        flash('A sala foi indisponibilizada com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=4))

    return render_template('salas/indisponibilizar_sala.html', 
                           title='Indisponibilizar Sala',
                           legend='Indisponibilizar Sala', form=form)


@salas.route("/<int:sala_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_sala(sala_id):
    # Impede uma sala de ser indevidamente excluída
    sala = Sala.recuperar_id(sala_id)
    if not sala.verificar_disponibilidade():
        if not sala.verificar_desabilitado():
            flash('Não é possível excluir uma sala solicitada ou em uso.', 'warning')
            return redirect(url_for('principal.inicio', tab=4))
    
    # Desativa o registro da sala
    sala.excluir()
    flash('A Sala foi excluída com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=4))


@salas.route("/<int:sala_id>/relatorios", methods=['GET', 'POST'])
@login_required
@admin_required
def relatorios(sala_id):
    # Recupera os relatórios do equipamento pela ID
    sala = Sala.recuperar_id(sala_id)
    relatorios = RelatorioSala.recuperar_tudo_sala(sala)

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
        relatorio = RelatorioSala.criar(sala_id, form)
        relatorio.inserir()
        flash('O relatório foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('salas.relatorios', sala_id=sala_id))

    return render_template('salas/novo_relatorio.html', 
                           title='Novo Relatório', sala_id=sala_id,
                           legend='Novo Relatório', form=form)


@salas.route("/<int:sala_id>/relatorios/<int:relatorio_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_relatorio(sala_id, relatorio_id):
    # Impede relatórios finalizados de serem atualizados
    relatorio = RelatorioSala.recuperar_id(relatorio_id)
    if not relatorio.verificar_aberto():
        flash('Este relatório já foi finalizado.', 'warning') 
        return redirect(url_for('salas.relatorios', sala_id=sala_id))
    
    # Valida o formulário e atualiza o relatório no banco de dados
    form = AtualizaRelatorioSalaForm()
    if form.validate_on_submit():
        relatorio.atualizar(form)
        flash('O relatório foi atualizado com sucesso!', 'success') 
        return redirect(url_for('salas.relatorios', sala_id=sala_id))
    elif request.method == 'GET':
        form.tipo.data = relatorio.tipo_relatorio.value
        form.conteudo.data = relatorio.conteudo
        form.manutencao.data = relatorio.manutencao
        form.reforma.data = relatorio.reforma
        form.detalhes.data = relatorio.detalhes
        form.finalizar.data = False

    return render_template('salas/atualizar_relatorio.html', 
                           title='Atualizar Relatório', sala_id=sala_id,
                           legend='Atualizar Relatório', form=form)
    