from datetime import datetime
import enum

from app import db, fuso_horario
from app.models.status import Status

# Classe enum para os tipos disponíveis de relatórios
class TipoRelatorio(enum.Enum):
    REVISAO = "Revisão"
    MANUTENCAO = "Manutenção"
    OUTRO = "Outro"

# Classe para registros de manutenção, revisão e outros
class Relatorio(db.Model):
    __tablename__ = 'relatorios'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    
    tipo_relatorio = db.Column(db.Enum(TipoRelatorio))
    conteudo = db.Column(db.Text, nullable=False)
    manutencao = db.Column(db.Boolean, nullable=False, default=False)
    detalhes = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(Status))
    data_abertura = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    data_finalizacao = db.Column(db.DateTime, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um relatório está associado a um usuário, e uma sala ou equipamento
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    tipo = db.Column(db.String(50)) # discriminador
    __mapper_args__ = {
        'polymorphic_identity': 'relatorios',
        'polymorphic_on': tipo
    }

# Classe específica para os relatórios de salas
class RelatorioSala(Relatorio):
    __tablename__ = 'relatorios_sala'
    
    id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), primary_key=True)
    reforma = db.Column(db.Boolean, nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'relatorios_sala'
    }

    # Um relatório está associado a um sala
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), 
                           nullable=True)
    
    sala = db.relationship('Sala', back_populates='relatorios')

    def __repr__(self):
        return f"Relatório #{self.id} - {self.tipo} - {self.status}"

# Classe específica para os relatórios de equipamentos
class RelatorioEquipamento(Relatorio):
    __tablename__ = 'relatorios_equipamento'
    
    id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), primary_key=True)
    defeito = db.Column(db.Boolean, nullable=False, default=False)
    
    # Um relatório está associado a um equipamento
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), 
                           nullable=True)

    equipamento = db.relationship('Equipamento', back_populates='relatorios')

    __mapper_args__ = {
        'polymorphic_identity': 'relatorios_equipamento'
    }
    
    def __repr__(self):
        return f"Relatório #{self.id} - {self.tipo} - {self.status}"
    