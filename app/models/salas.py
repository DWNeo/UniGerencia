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
    
    # Recupera a sala pela ID e retorna erro 404 caso contrário
    def recupera_id(sala_id):
        return Sala.query.filter_by(id=sala_id).filter_by(ativo=True).first_or_404()
    
    # Verifica se uma sala está disponível
    def verifica_disponibilidade(sala):
        if sala.status.name == 'ABERTO':
            return True
        else:
            return False
    
    # Verifica se uma sala está desabilitada
    def verifica_desabilitado(sala):
        if sala.status.name == 'DESABILITADO':
            return True
        else:
            return False    
        '''
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
        db.session.commit()'''
        
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
    
    # Recupera todas os setores presentes no banco de dados
    def recupera_tudo():
        return Setor.query.filter_by(ativo=True).all()
    
    # Recupera o setor pela ID e retorna erro 404 caso contrário
    def recupera_id(setor_id):
        return Setor.query.filter_by(id=setor_id).filter_by(ativo=True).first_or_404()
    
    def __repr__(self):
        return f"{self.name} - Quantidade Disponível: {self.qtd_disponivel}"
    