from datetime import datetime

from app import db, fuso_horario
from app.models.status import Status

# Classe para as solicitações de equipamentos e salas
class Solicitacao(db.Model):
    __tablename__ = 'solicitacoes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status), default=Status.ABERTO.name)
    data_abertura = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_inicio_pref = db.Column(db.Date, nullable=False)
    data_fim_pref = db.Column(db.Date, nullable=False)
    data_retirada = db.Column(db.DateTime, nullable=True)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    data_cancelamento = db.Column(db.DateTime, nullable=True)
    data_finalizacao = db.Column(db.DateTime, nullable=True)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    descricao = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    tipo = db.Column(db.String(20), nullable=False)

    # Uma solicitação está associada a um usuário e um turno
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos.id'), 
                           nullable=False)
    
    turno = db.relationship('Turno', back_populates='solicitacoes')

    # Recupera todas as solicitações presentes no banco de dados
    def recupera_todas():
        return Solicitacao.query.filter_by(ativo=True).all()
        
    # Recupera as últimas solicitações de um usuário específico
    def recupera_autor_limite(usuario, limite):
        return Solicitacao.query.filter_by(autor=usuario).filter_by(
            ativo=True).order_by(Solicitacao.id.desc()).limit(limite)

    def atualiza_status_pendente(solicitacao):
        solicitacao.status = 'PENDENTE'
        if solicitacao.tipo == 'Equipamento':
            for equipamento in solicitacao.equipamentos:
                equipamento.status = 'PENDENTE'
        if solicitacao.tipo == 'Sala':
            for sala in solicitacao.salas:
                sala.status = 'PENDENTE'     
        db.session.commit()
    
    __mapper_args__ = {
        'polymorphic_identity': 'solicitacoes',
        'polymorphic_on': tipo
    }

    def __repr__(self):
        return f"Solicitação #{self.id} - {self.tipo} - {self.status.value}"
 
# Tabela que associa as solicitações às salas
solicitacao_s = db.Table('solicitacao_s',
    db.Column('solicitacao_sala_id', db.Integer, db.ForeignKey('solicitacoes_salas.id'), 
              primary_key=True),
    db.Column('sala_id', db.Integer, db.ForeignKey('salas.id'), 
              primary_key=True)
)

# Tabela que associam as solicitações aos equipamentos
solicitacao_e = db.Table('solicitacao_e',
    db.Column('solicitacao_equipamento_id', db.Integer, db.ForeignKey('solicitacoes_equipamentos.id'), 
              primary_key=True),
    db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamentos.id'), 
              primary_key=True)
)

# Classe específica para as solicitações de salas
class SolicitacaoSala(Solicitacao):
    __tablename__ = 'solicitacoes_salas'
    
    id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), primary_key=True)

    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    
    # Pode estar associada a múltiplas salas de um único setor
    setor = db.relationship('Setor', back_populates='solicitacoes')
    salas = db.relationship('Sala', secondary= solicitacao_s, 
                                    back_populates='solicitacoes')
    
    __mapper_args__ = {
        'polymorphic_identity': 'Sala',
    }

# Classe específica para as solicitações de equipamentos
class SolicitacaoEquipamento(Solicitacao):
    __tablename__ = 'solicitacoes_equipamentos'
    
    id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), primary_key=True)

    tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipos_equipamento.id'), 
                           nullable=True)
    
    # Pode estar associada a múltiplos equipamentos de um único tipo
    equipamentos = db.relationship('Equipamento', secondary=solicitacao_e, 
                                   back_populates='solicitacoes')
    tipo_eqp = db.relationship('TipoEquipamento', back_populates='solicitacoes')

    __mapper_args__ = {
        'polymorphic_identity': 'Equipamento'
    }

# Classe para os turnos possíveis para solicitações
class Turno(db.Model):
    __tablename__ = 'turnos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    data_inicio = db.Column(db.Time, nullable=False)
    data_fim = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um turno pode estar associado a múltiplas solicitações
    solicitacoes = db.relationship('Solicitacao', back_populates='turno')
    
    def __repr__(self):
        return f"{self.name} - Início: {self.data_inicio} - Fim: {self.data_fim}"
    