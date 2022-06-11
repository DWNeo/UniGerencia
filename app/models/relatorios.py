from datetime import datetime
import enum

from flask_login import current_user

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
    status = db.Column(db.Enum(Status), server_default='ABERTO')
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
        'polymorphic_identity': 'RELATORIO',
        'polymorphic_on': tipo
    }
    
    def __repr__(self):
        return f"Relatório #{self.id} - {self.tipo} - {self.status}"
    
    # Verifica se um relatório está em aberto
    def verificar_aberto(self):
        if self.status.name == 'ABERTO':
            return True
        else:
            return False
        
    # Insere um novo relatório no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
        
    # Atualiza um relatório existente no banco de dados
    def atualizar(self, form):
        # Atualiza as datas dependendo do status selecionado
        if form.finalizar.data == True:
            self.status = 'FECHADO'
            self.data_finalizacao = datetime.now().astimezone(fuso_horario)
        else:
            self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        self.conteudo = form.conteudo.data
        self.detalhes = form.detalhes.data
        db.session.commit()
    

# Classe para os relatórios de salas
class RelatorioSala(Relatorio):
    __tablename__ = 'relatorios_sala'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), primary_key=True)
    reforma = db.Column(db.Boolean, nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'SALA'
    }

    # Um relatório está associado a um sala
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), 
                           nullable=True)
    
    sala = db.relationship('Sala', back_populates='relatorios')
    
    # Recupera o relatório pela ID e retorna erro 404 caso contrário
    def recuperar_id(relatorio_id):
        return RelatorioSala.query.filter_by(
            id=relatorio_id).filter_by(ativo=True).first_or_404()
        
    # Recupera todos os relatórios de uma sala
    def recuperar_tudo_sala(sala):
        return RelatorioSala.query.filter_by(
            sala_id=sala.id).filter_by(ativo=True).all()
    
    # Cria um novo relatório de sala para ser inserido
    def criar(sala_id, form):
        if form.finalizar.data == True:
            status = 'FECHADO'
            data_finalizacao = datetime.now().astimezone(fuso_horario)
        else:
            status = 'ABERTO'
            data_finalizacao = None
        return RelatorioSala(tipo_relatorio=form.tipo.data, 
                             conteudo=form.conteudo.data,
                             manutencao=form.manutencao.data,
                             reforma=form.reforma.data,
                             detalhes=form.detalhes.data,
                             status=status,
                             data_finalizacao=data_finalizacao,
                             usuario_id=current_user.id,
                             sala_id=sala_id)

    def verificar_aberto(self):
        return super().verificar_aberto()
    
    def inserir(self):
        return super().inserir()
    
    def atualizar(self, form):
        return super().atualizar(form)


# Classe para os relatórios de equipamentos
class RelatorioEquipamento(Relatorio):
    __tablename__ = 'relatorios_equipamento'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), primary_key=True)
    defeito = db.Column(db.Boolean, nullable=False, default=False)
    
    # Um relatório está associado a um equipamento
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), 
                           nullable=True)

    equipamento = db.relationship('Equipamento', back_populates='relatorios')

    __mapper_args__ = {
        'polymorphic_identity': 'EQUIPAMENTO'
    }
    
    # Recupera o relatório pela ID e retorna erro 404 caso contrário
    def recuperar_id(relatorio_id):
        return RelatorioEquipamento.query.filter_by(
            id=relatorio_id).filter_by(ativo=True).first_or_404()
        
    # Recupera todas os relatórios de um equipamento
    def recuperar_tudo_eqp(equipamento):
        return RelatorioEquipamento.query.filter_by(
            equipamento_id=equipamento.id).filter_by(ativo=True).all()
        
    # Cria um novo relatório de equipamento para ser inserido
    def criar(eqp_id, form):
        if form.finalizar.data == True:
            status = 'FECHADO'
            data_finalizacao = datetime.now().astimezone(fuso_horario)
        else:
            status = 'ABERTO'
            data_finalizacao = None
        return RelatorioEquipamento(conteudo=form.conteudo.data,
                                    manutencao=form.manutencao.data, 
                                    defeito=form.defeito.data,
                                    detalhes=form.detalhes.data,
                                    status=status,
                                    tipo_relatorio=form.tipo.data,
                                    data_finalizacao=data_finalizacao,
                                    usuario_id=current_user.id,
                                    equipamento_id=eqp_id)
    
    def verificar_aberto(self):
        return super().verificar_aberto()
    
    def inserir(self):
        return super().inserir()
        
    def atualizar(self, form):
        return super().atualizar(form)
    