from datetime import datetime

from flask import (render_template, url_for, flash, 
                   redirect, request, Blueprint)
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import (Equipamento, RelatorioEquipamento, SolicitacaoEquipamento, 
                        TipoEquipamento, Solicitacao)
from app.forms.equipamentos import (EquipamentoForm, IndisponibilizaEquipamentoForm,
                                    AtualizaEquipamentoForm, TipoEquipamentoForm,
                                    RelatorioEquipamentoForm, AtualizaRelatorioEquipamentoForm)
from app.utils import admin_required

equipamentos = Blueprint('equipamentos', __name__)


@equipamentos.route("/<int:eqp_id>")
@login_required
@admin_required
def equipamento(eqp_id):
    # Recupera o equipamento por ID
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()

    # Recupera as últimas solicitações associadas ao equipamento
    solicitacoes = Solicitacao.query.filter(
        SolicitacaoEquipamento.equipamentos.contains(equipamento)).filter_by(
        ativo=True).order_by(SolicitacaoEquipamento.id.desc()).limit(5)

    # Renderiza o template
    return render_template('equipamentos/equipamento.html', 
                           title=equipamento, equipamento=equipamento,
                           solicitacoes=solicitacoes)


@equipamentos.route("/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_equipamento():
    # Preenche a lista de seleção de tipos de equipamento 
    # de acordo com o retornado pelo banco de dados
    form = EquipamentoForm()
    tipos_eqp = TipoEquipamento.query.filter_by(
        ativo=True).all()
    lista_tipos=[(tipo.id, tipo.nome) for tipo in tipos_eqp]
    if lista_tipos:
        form.tipo_eqp.choices = lista_tipos
    else:
        flash('Não há tipos de equipamento cadastrados.', 'warning')
        return redirect(url_for('principal.inicio', tab=3))
    
    # Valida os dados do formulário enviado e insere um 
    # novo registro de equipamento no banco de dados
    if form.validate_on_submit():
        # Recupera o tipo de equipamento e adiciona um ao
        # número de equipamentos disponíveis daquele tipo
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
    # Valida os dados do formulário enviado e insere um 
    # novo registro de tipo de equipamento no banco de dados
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
    # Recupera o equipamento pela ID
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()

    # Valida o formulário enviado e atualiza o registro
    # do equipamento no banco de dados de acordo com ele
    form = AtualizaEquipamentoForm()
    if form.validate_on_submit():
        equipamento.descricao = form.descricao.data
        equipamento.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        flash('O equipamento foi atualizado com sucesso!', 'success')  
        return redirect(url_for('principal.inicio', tab=3))
    elif request.method == 'GET':
        form.descricao.data = equipamento.descricao

    return render_template('equipamentos/atualizar_equipamento.html', 
                           title='Atualizar Equipamento',
                           legend='Atualizar Equipamento',
                           form=form)


@equipamentos.route("/<int:eqp_id>/disponibilizar", methods=['GET', 'POST'])
@login_required
@admin_required
def disponibiliza_equipamento(eqp_id):
    # Valida os dados do formulário enviado e altera o status
    # do equipamento escolhido para 'Disponível'
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()
    
    # Verifica se o equipamento está indisponível
    if equipamento.status.name == 'ABERTO':
        flash('Esse equipamento já está disponível.', 'warning')
        return redirect(url_for('principal.inicio', tab=3))

    # Altera o registro do equipamento
    equipamento.motivo_indisponibilidade = None
    equipamento.status = 'ABERTO'
    equipamento.data_atualizacao = datetime.now().astimezone(fuso_horario)

    # Aumenta a quantidade de equipamentos disponíveis do tipo
    tipo_eqp = TipoEquipamento.query.filter_by(
        id=equipamento.tipo_eqp_id).filter_by(ativo=True).first()
    tipo_eqp.qtd_disponivel += 1

    db.session.commit()
    flash('O equipamento foi disponibilizado com sucesso!', 'success') 
    return redirect(url_for('principal.inicio', tab=3))


@equipamentos.route("/<int:eqp_id>/indisponibilizar", methods=['GET', 'POST'])
@login_required
@admin_required
def indisponibiliza_equipamento(eqp_id):
    # Valida os dados do formulário enviado e altera o status
    # do equipamento escolhido para 'Indisponível'
    form = IndisponibilizaEquipamentoForm()
    if form.validate_on_submit():
        equipamento = Equipamento.query.filter_by(
            id=eqp_id).filter_by(ativo=True).first_or_404()
        
        # Verifica se o equipamento está disponível
        if equipamento.status.name != 'ABERTO':
            flash('Você não pode tornar este equipamento indisponível.', 'warning')
            return redirect(url_for('principal.inicio', tab=3))

        # Altera o registro do equipamento
        equipamento.motivo_indisponibilidade = form.motivo.data
        equipamento.status = 'DESABILITADO'
        equipamento.data_atualizacao = datetime.now().astimezone(fuso_horario)

        # Diminui a quantidade de equipamentos disponíveis do tipo
        tipo_eqp = TipoEquipamento.query.filter_by(
            id=equipamento.tipo_eqp_id).filter_by(ativo=True).first()
        tipo_eqp.qtd_disponivel -= 1

        db.session.commit()
        flash('O equipamento foi indisponibilizado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=3))

    return render_template('equipamentos/indisponibilizar_equipamento.html', 
                           title='Indisponibilizar Equipamento',
                           legend='Indisponibilizar Equipamento', form=form)


@equipamentos.route("/<int:eqp_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_equipamento(eqp_id):
    # Recupera o equipamento pela ID
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()
    
    # Impede um equipamento de ser indevidamente excluído
    if equipamento.status.name != 'ABERTO' and equipamento.status.name != 'DESABILITADO':
        flash('Não é possível excluir uma equipamento\
               solicitado ou em uso.', 'warning')
        return redirect(url_for('principal.inicio', tab=3))

    # Diminui a quantidade de equipamentos disponíveis do tipo
    # caso o status do equipamento esteja contando como um
    if equipamento.status.name == 'ABERTO':
        tipo_eqp = TipoEquipamento.query.filter_by(
            id=equipamento.tipo_eqp_id).filter_by(ativo=True).first()
        tipo_eqp.qtd_disponivel -= 1

    # Desativa o registro do equipamento
    equipamento.ativo = False
    db.session.commit()
    flash('O equipamento foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=3))

    
@equipamentos.route("/<int:eqp_id>/relatorios", methods=['GET', 'POST'])
@login_required
@admin_required
def relatorios(eqp_id):
    # Recupera os relatórios do equipamento pela ID
    equipamento = Equipamento.query.filter_by(
        id=eqp_id).filter_by(ativo=True).first_or_404()
    relatorios = RelatorioEquipamento.query.filter_by(
        equipamento_id=equipamento.id).filter_by(ativo=True).all()

    return render_template('equipamentos/relatorios.html', 
                           title='Relatórios do Equipamento',
                           legend='Relatórios do Equipamento',
                           relatorios=relatorios, eqp_id=eqp_id)


@equipamentos.route("/<int:eqp_id>/relatorios/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_relatorio(eqp_id):
    # Valida o formulário e insere o novo relatório no banco de dados
    form = RelatorioEquipamentoForm()
    if form.validate_on_submit():
        status = 'ABERTO'

        relatorio = RelatorioEquipamento(conteudo=form.conteudo.data,
                              manutencao=form.manutencao.data, 
                              defeito=form.defeito.data,
                              detalhes=form.detalhes.data,
                              status = status,
                              tipo_relatorio=form.tipo.data,
                              usuario_id=current_user.id,
                              equipamento_id=eqp_id)
        db.session.add(relatorio)
        db.session.commit()
        flash('O relatório foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('equipamentos.relatorios', eqp_id=eqp_id))

    return render_template('equipamentos/novo_relatorio.html', 
                           title='Novo Relatório', eqp_id=eqp_id,
                           legend='Novo Relatório', form=form)


@equipamentos.route("/<int:eqp_id>/relatorios/<int:id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_relatorio(eqp_id, id):
    # Recupera o relatório pela ID
    relatorio = RelatorioEquipamento.query.filter_by(
        id=id).filter_by(ativo=True).first_or_404()

    # Impede relatórios finalizados de serem atualizados
    if relatorio.status.name == 'FECHADO':
        flash('Este relatório já foi finalizado.', 'success') 
        return redirect(url_for('equipamentos.relatorios', eqp_id=eqp_id))

    # Valida o formulário e atualiza o relatório no banco de dados
    form = AtualizaRelatorioEquipamentoForm()
    if form.validate_on_submit():
        relatorio.conteudo = form.conteudo.data
        relatorio.detalhes = form.detalhes.data
        relatorio.status = form.status.data

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
        return redirect(url_for('equipamentos.relatorios', eqp_id=eqp_id))
    elif request.method == 'GET':
        form.tipo.data = relatorio.tipo_relatorio.value
        form.conteudo.data = relatorio.conteudo
        form.manutencao.data = relatorio.manutencao
        form.defeito.data = relatorio.defeito
        form.detalhes.data = relatorio.detalhes
        form.status.data = False

    return render_template('equipamentos/atualizar_relatorio.html', 
                           title='Atualizar Relatório', eqp_id=eqp_id,
                           legend='Atualizar Relatório', form=form)
    