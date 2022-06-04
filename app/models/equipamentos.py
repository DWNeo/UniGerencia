from datetime import datetime
import enum

from app import db, fuso_horario
from app.models.status import Status
from app.models.solicitacoes import solicitacao_e

# Classe para os equipamentos disponíveis para solicitações
class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.String(50), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(Status), default=Status.ABERTO.name)
    motivo_indisponibilidade = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um equipamento pertence a um tipo em específico
    tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipos_equipamento.id'), 
                            nullable=False)

    # Um equipamento faz parte de diferentes solicitações e relatórios
    tipo_eqp = db.relationship('TipoEquipamento', back_populates='equipamentos')
    solicitacoes = db.relationship('SolicitacaoEquipamento', secondary=solicitacao_e, 
                                   back_populates='equipamentos')
    relatorios = db.relationship('RelatorioEquipamento', back_populates='equipamento')
        
    # Recupera todas os equipamentos presentes no banco de dados
    def recupera_tudo():
        return Equipamento.query.filter_by(ativo=True).all()
    
    # Recupera o equipamento pela ID e retorna erro 404 caso contrário
    def recupera_id(eqp_id):
        return Equipamento.query.filter_by(id=eqp_id).filter_by(ativo=True).first_or_404()
    
    # Verifica se um equipamento está disponível
    def verifica_disponibilidade(equipamento):
        if equipamento.status.name == 'ABERTO':
            return True
        else:
            return False
    
    # Verifica se um equipamento está desabilitado
    def verifica_desabilitado(equipamento):
        if equipamento.status.name == 'DESABILITADO':
            return True
        else:
            return False    
        
    # Cria um novo equipamento para ser inserido
    def cria(form):
        return Equipamento(patrimonio=form.patrimonio.data, 
                           descricao=form.descricao.data, 
                           tipo_eqp_id=form.tipo_eqp.data)
        
    # Insere um novo equipamento no banco de dados
    def insere(equipamento):
        tipo_eqp = TipoEquipamento.recupera_id(equipamento.tipo_eqp_id)
        TipoEquipamento.atualiza_qtd(tipo_eqp, +1)
        db.session.add(equipamento)
        db.session.commit()
        
    # Atualiza um equipamento existente no banco de dados
    def atualiza(equipamento, form):
        equipamento.descricao = form.descricao.data
        equipamento.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Disponibiliza novamente o equipamento para solicitações    
    def disponibiliza(equipamento):
        equipamento.motivo_indisponibilidade = None
        equipamento.status = 'ABERTO'
        equipamento.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Indisponibiliza o equipamento para solicitações    
    def indisponibiliza(equipamento, motivo):
        equipamento.motivo_indisponibilidade = motivo
        equipamento.status = 'DESABILITADO'
        equipamento.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Desativa o registro de um equipamento no banco de dados
    def exclui(equipamento):
        if equipamento.status.name == 'ABERTO':
            TipoEquipamento.atualiza_qtd(equipamento.tipo_eqp, -1)
        equipamento.ativo = False
        db.session.commit()
        
    def __repr__(self):
        return f"{self.patrimonio} - {self.descricao}"

# Classe para os tipos possíveis de equipamentos
class TipoEquipamento(db.Model):
    __tablename__ = 'tipos_equipamento'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)
    qtd_disponivel = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um tipo está associado a múltiplos equipamentos e solicitações
    equipamentos = db.relationship('Equipamento', back_populates='tipo_eqp')
    solicitacoes = db.relationship('SolicitacaoEquipamento', back_populates='tipo_eqp')

    # Recupera todas os tipos de equipamento presentes no banco de dados
    def recupera_tudo():
        return TipoEquipamento.query.filter_by(ativo=True).all()
    
    # Recupera o tipo pela ID e retorna erro 404 caso contrário
    def recupera_id(tipo_eqp_id):
        return TipoEquipamento.query.filter_by(id=tipo_eqp_id).filter_by(ativo=True).first_or_404()
    
    # Cria um novo tipo para ser inserido
    def cria(form):
        return TipoEquipamento(nome=form.nome.data)
    
    # Insere um novo tipo no banco de dados
    def insere(tipo_eqp):
        db.session.add(tipo_eqp)
        db.session.commit()
    
    # Atualiza a quantidade de equipamentos disponíveis de um tipo
    def atualiza_qtd(tipo_eqp, qtd):
        tipo_eqp.qtd_disponivel += qtd
        db.session.commit()
    
    def __repr__(self):
        return f"{self.nome} - Qtd. Disponível: {self.qtd_disponivel}"
    