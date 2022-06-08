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
        
    def __repr__(self):
        return f"{self.patrimonio} - {self.descricao}"
    
    # Recupera todas os equipamentos presentes no banco de dados
    def recuperar_tudo():
        return Equipamento.query.filter_by(ativo=True).all()
    
    # Recupera o equipamento pela ID e retorna erro 404 caso contrário
    def recuperar_id(eqp_id):
        return Equipamento.query.filter_by(id=eqp_id).filter_by(ativo=True).first_or_404()
    
    # Recupera todos os equipamentos disponíveis de um tipo
    def recuperar_disponivel_tipo(tipo_eqp_id):
        return Equipamento.query.filter_by(status='ABERTO').filter_by(
            ativo=True).filter_by(tipo_eqp_id=tipo_eqp_id).all()
        
    # Recupera o primeiro equipamento pelo patrimônio
    def recupera_primeiro_patrimonio(patrimonio):
        return Equipamento.query.filter_by(patrimonio=patrimonio).first()
    
    # Verifica se um equipamento está disponível
    def verificar_disponibilidade(self):
        if self.status.name == 'ABERTO':
            return True
        else:
            return False
    
    # Verifica se um equipamento está desabilitado
    def verificar_desabilitado(self):
        if (self.status.name == 'DESABILITADO' or
            self.status.name == 'EMMANUTENCAO'):
            return True
        else:
            return False    
        
    # Cria um novo equipamento para ser inserido
    def criar(form):
        return Equipamento(patrimonio=form.patrimonio.data, 
                           descricao=form.descricao.data, 
                           tipo_eqp_id=form.tipo_eqp.data)
        
    # Insere um novo equipamento no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
        
    # Atualiza um equipamento existente no banco de dados
    def atualizar(self, form):
        self.descricao = form.descricao.data
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Disponibiliza novamente o equipamento para solicitações    
    def disponibilizar(self):
        self.motivo_indisponibilidade = None
        self.status = 'ABERTO'
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Indisponibiliza o equipamento para solicitações    
    def indisponibilizar(self, form):
        self.motivo_indisponibilidade = form.motivo.data
        self.status = 'DESABILITADO'
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Desativa o registro de um equipamento no banco de dados
    def excluir(self):
        self.ativo = False
        db.session.commit()


# Classe para os tipos possíveis de equipamentos
class TipoEquipamento(db.Model):
    __tablename__ = 'tipos_equipamento'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um tipo está associado a múltiplos equipamentos e solicitações
    equipamentos = db.relationship('Equipamento', back_populates='tipo_eqp')
    solicitacoes = db.relationship('SolicitacaoEquipamento', back_populates='tipo_eqp')

    def __repr__(self):
        return f"{self.nome} - Qtd. Disponível: {self.contar()}"
    
    # Recupera todas os tipos de equipamento presentes no banco de dados
    def recuperar_tudo():
        return TipoEquipamento.query.filter_by(ativo=True).all()
    
    # Recupera o tipo pela ID e retorna erro 404 caso contrário
    def recuperar_id(tipo_eqp_id):
        return TipoEquipamento.query.filter_by(id=tipo_eqp_id).filter_by(ativo=True).first_or_404()
    
    # Recupera o primeiro tipo de equipamento pelo nome
    def recupera_primeiro_nome(nome):
        return TipoEquipamento.query.filter_by(nome=nome).first()
    
    # Cria um novo tipo para ser inserido
    def criar(form):
        return TipoEquipamento(nome=form.nome.data)
    
    # Insere um novo tipo no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
        
    # Retorna o número de equipamentos disponíveis de um tipo
    def contar(self):
        return Equipamento.query.filter_by(status='ABERTO').filter_by(
            tipo_eqp=self).filter_by(ativo=True).count()
    