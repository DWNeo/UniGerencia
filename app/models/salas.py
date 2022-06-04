from datetime import datetime

from app import db, fuso_horario
from app.models.status import Status
from app.models.solicitacoes import solicitacao_s

# Classe para as salas disponíveis para solicitações
class Sala(db.Model):
    __tablename__ = 'salas'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    qtd_aluno = db.Column(db.Integer, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(Status), default=Status.ABERTO.name)
    motivo_indisponibilidade = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Uma sala pertence a um setor específico
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    
    # Uma sala faz parte de diferentes solicitações e relatórios
    solicitacoes = db.relationship('SolicitacaoSala', secondary=solicitacao_s, 
                                   back_populates='salas')
    relatorios = db.relationship('RelatorioSala', back_populates='sala')
    setor = db.relationship('Setor', back_populates='salas')  

    # Recupera todas as salas presentes no banco de dados
    def recupera_tudo():
        return Sala.query.filter_by(ativo=True).all()
        
    def __repr__(self):
        return f"{self.numero} - {self.setor.name} - Qtde. Alunos: {self.qtd_aluno}"

# Classe para os diferentes setores de salas
class Setor(db.Model):
    __tablename__ = 'setores'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    qtd_disponivel = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um setor pode estar associado a muitas salas e solicitações
    solicitacoes = db.relationship('SolicitacaoSala', back_populates='setor')    
    salas = db.relationship('Sala', back_populates='setor')
    
    def __repr__(self):
        return f"{self.name} - Quantidade Disponível: {self.qtd_disponivel}"
    