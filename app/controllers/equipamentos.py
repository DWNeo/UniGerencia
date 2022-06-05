from flask import (render_template, url_for, flash, 
                   redirect, request, Blueprint)
from flask_login import login_required

from app.models import (Equipamento, RelatorioEquipamento, TipoEquipamento, 
                        Solicitacao, admin_required)
from app.forms.equipamentos import (EquipamentoForm, IndisponibilizaEquipamentoForm,
                                    AtualizaEquipamentoForm, TipoEquipamentoForm,
                                    RelatorioEquipamentoForm, AtualizaRelatorioEquipamentoForm)

equipamentos = Blueprint('equipamentos', __name__)


@equipamentos.route("/<int:eqp_id>")
@login_required
@admin_required
def equipamento(eqp_id):
    # Recupera as 5 últimas solicitações associadas ao equipamento
    equipamento = Equipamento.recupera_id(eqp_id)
    solicitacoes = Solicitacao.recupera_ultimas_eqp(equipamento, 5)
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
    tipos_eqp = TipoEquipamento.recupera_tudo()
    lista_tipos=[(tipo.id, tipo.nome) for tipo in tipos_eqp]
    if lista_tipos:
        form.tipo_eqp.choices = lista_tipos
    else:
        flash('Não há tipos de equipamento cadastrados.', 'warning')
        return redirect(url_for('principal.inicio', tab=3))
    
    # Valida os dados do formulário enviado e insere um 
    # novo registro de equipamento no banco de dados
    if form.validate_on_submit():
        equipamento = Equipamento.cria(form)
        equipamento.insere()
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
        tipo_eqp = TipoEquipamento.cria(form)
        tipo_eqp.insere()
        flash('O tipo de equipamento foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=3))

    return render_template('equipamentos/novo_tipo_equipamento.html', 
                           title='Novo Tipo de Equipamento', form=form,
                           legend='Novo Tipo de Equipamento')


@equipamentos.route("/<int:eqp_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_equipamento(eqp_id):
    # Valida o formulário enviado e atualiza o registro
    # do equipamento no banco de dados de acordo com ele
    equipamento = Equipamento.recupera_id(eqp_id)
    form = AtualizaEquipamentoForm()
    if form.validate_on_submit():
        equipamento.atualiza(form)
        flash('O equipamento foi atualizado com sucesso!', 'success')  
        return redirect(url_for('principal.inicio', tab=3))
    elif request.method == 'GET':
        form.descricao.data = equipamento.descricao

    return render_template('equipamentos/atualizar_equipamento.html', 
                           title='Atualizar Equipamento', form=form,
                           legend='Atualizar Equipamento')


@equipamentos.route("/<int:eqp_id>/disponibilizar", methods=['GET', 'POST'])
@login_required
@admin_required
def disponibiliza_equipamento(eqp_id):
    # Valida os dados do formulário enviado e altera o status
    # do equipamento escolhido para 'Disponível'
    equipamento = Equipamento.recupera_id(eqp_id)
    if equipamento.verifica_disponibilidade():
        flash('Esse equipamento já está disponível.', 'warning')
        return redirect(url_for('principal.inicio', tab=3))

    # Atualiza os registros do equipamento e do seu tipo
    equipamento.disponibiliza()
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
        equipamento = Equipamento.recupera_id(eqp_id)
        if not equipamento.verifica_disponibilidade():
            flash('Você não pode tornar este equipamento indisponível.', 'warning')
            return redirect(url_for('principal.inicio', tab=3))

        # Atualiza os registros do equipamento e do seu tipo
        equipamento.indisponibiliza(form)
        flash('O equipamento foi indisponibilizado com sucesso!', 'success') 
        return redirect(url_for('principal.inicio', tab=3))

    return render_template('equipamentos/indisponibilizar_equipamento.html', 
                           title='Indisponibilizar Equipamento',
                           legend='Indisponibilizar Equipamento', form=form)


@equipamentos.route("/<int:eqp_id>/excluir", methods=['POST'])
@login_required
@admin_required
def exclui_equipamento(eqp_id):
    # Impede um equipamento de ser indevidamente excluído
    equipamento = Equipamento.recupera_id(eqp_id)
    if not equipamento.verifica_disponibilidade():
        if not equipamento.verifica_desabilitado():
            flash('Não é possível excluir uma equipamento\
                solicitado ou em uso.', 'warning')
            return redirect(url_for('principal.inicio', tab=3))

    # Desativa o registro do equipamento
    equipamento.exclui()
    flash('O equipamento foi excluído com sucesso!', 'success')
    return redirect(url_for('principal.inicio', tab=3))

    
@equipamentos.route("/<int:eqp_id>/relatorios", methods=['GET', 'POST'])
@login_required
@admin_required
def relatorios(eqp_id):
    # Recupera todos os relatórios do equipamento
    equipamento = Equipamento.recupera_id(eqp_id)
    relatorios = RelatorioEquipamento.recupera_tudo_eqp(equipamento)

    return render_template('equipamentos/relatorios.html', 
                           title='Relatórios do Equipamento',
                           legend='Relatórios do Equipamento',
                           relatorios=relatorios, eqp_id=eqp_id)


@equipamentos.route("/<int:eqp_id>/relatorios/novo", methods=['GET', 'POST'])
@login_required
@admin_required
def novo_relatorio(eqp_id):
    # Valida o formulário e insere o novo relatório no banco de dados
    equipamento = Equipamento.recupera_id(eqp_id)
    form = RelatorioEquipamentoForm()
    if form.validate_on_submit():
        relatorio = RelatorioEquipamento.cria(equipamento.id, form)
        relatorio.insere()
        flash('O relatório foi cadastrado com sucesso!', 'success') 
        return redirect(url_for('equipamentos.relatorios', eqp_id=eqp_id))

    return render_template('equipamentos/novo_relatorio.html', 
                           title='Novo Relatório', eqp_id=eqp_id,
                           legend='Novo Relatório', form=form)


@equipamentos.route("/<int:eqp_id>/relatorios/<int:relatorio_id>/atualizar", methods=['GET', 'POST'])
@login_required
@admin_required
def atualiza_relatorio(eqp_id, relatorio_id):
    # Impede relatórios finalizados de serem atualizados
    relatorio = RelatorioEquipamento.recupera_id(relatorio_id)
    if not relatorio.verifica_aberto():
        flash('Este relatório já foi finalizado.', 'warning') 
        return redirect(url_for('equipamentos.relatorios', eqp_id=eqp_id))

    # Valida o formulário e atualiza o relatório no banco de dados
    form = AtualizaRelatorioEquipamentoForm()
    if form.validate_on_submit():
        relatorio.atualiza(form)
        flash('O relatório foi atualizado com sucesso!', 'success') 
        return redirect(url_for('equipamentos.relatorios', eqp_id=eqp_id))
    elif request.method == 'GET':
        form.tipo.data = relatorio.tipo_relatorio.value
        form.conteudo.data = relatorio.conteudo
        form.manutencao.data = relatorio.manutencao
        form.defeito.data = relatorio.defeito
        form.detalhes.data = relatorio.detalhes
        form.finalizar.data = False

    return render_template('equipamentos/atualizar_relatorio.html', 
                           title='Atualizar Relatório', eqp_id=eqp_id,
                           legend='Atualizar Relatório', form=form)
    