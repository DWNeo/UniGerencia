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

    def __repr__(self):
        return f"{self.numero} - {self.setor.name} - Qtde. Alunos: {self.qtd_aluno}"
    
    # Recupera todas as salas presentes no banco de dados
    def recuperar_tudo():
        return Sala.query.filter_by(ativo=True).all()
    
    # Recupera todas as salas disponíveis em um setor
    def recuperar_disponivel_setor(setor_id):
        return Sala.query.filter_by(setor_id=setor_id).filter_by(
               status='ABERTO').filter_by(ativo=True).all()
    
    # Recupera a sala pela ID e retorna erro 404 caso contrário
    def recuperar_id(sala_id):
        return Sala.query.filter_by(id=sala_id).filter_by(ativo=True).first_or_404()
    
    # Recupera a primeira sala pelo número
    def recupera_primeiro_numero(numero):
        return Sala.query.filter_by(numero=numero).first()
    
    # Verifica se uma sala está disponível
    def verificar_disponibilidade(self):
        if self.status.name == 'ABERTO':
            return True
        else:
            return False
    
    # Verifica se uma sala está desabilitada
    def verificar_desabilitado(self):
        if self.status.name == 'DESABILITADO':
            return True
        else:
            return False    
        
    # Cria uma nova sala para ser inserido
    def criar(form):
        return Sala(numero=form.numero.data, setor_id=form.setor.data, 
                    qtd_aluno=form.qtd_aluno.data)
        
    # Insere uma nova sala no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
        
    # Atualiza uma sala existente no banco de dados
    def atualizar(self, form):
        self.setor_id = form.setor.data
        self.qtd_aluno = form.qtd_aluno.data
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
    
    # Verifica se um equipamento está disponível
    def verificar_disponibilidade(self):
        if self.status.name == 'ABERTO':
            return True
        else:
            return False
        
    # Verifica se uma sala está desabilitada
    def verificar_desabilitado(self):
        if (self.status.name == 'DESABILITADO' or
            self.status.name == 'EMMANUTENCAO'):
            return True
        else:
            return False 
        
    # Disponibiliza novamente a sala para solicitações    
    def disponibilizar(self):
        self.motivo_indisponibilidade = None
        self.status = 'ABERTO'
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Indisponibiliza a sala para solicitações    
    def indisponibilizar(self, form):
        self.motivo_indisponibilidade = form.motivo.data
        self.status = 'DESABILITADO'
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()

    # Desativa o registro de uma sala no banco de dados
    def excluir(self):
        self.ativo = False
        db.session.commit()

# Classe para os diferentes setores de salas
class Setor(db.Model):
    __tablename__ = 'setores'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um setor pode estar associado a muitas salas e solicitações
    solicitacoes = db.relationship('SolicitacaoSala', back_populates='setor')    
    salas = db.relationship('Sala', back_populates='setor')
    
    # Recupera todas os setores presentes no banco de dados
    def recuperar_tudo():
        return Setor.query.filter_by(ativo=True).all()
    
    # Recupera o setor pela ID e retorna erro 404 caso contrário
    def recuperar_id(setor_id):
        return Setor.query.filter_by(id=setor_id).filter_by(ativo=True).first_or_404()
    
    # Cria um novo setor para ser inserido
    def criar(form):
        return Setor(name=form.nome.data)
        
    # Insere um novo setor no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
    
    # Retorna o número de salas disponíveis de um setor
    def contar(self):
        return Sala.query.filter_by(status='ABERTO').filter_by(
            setor=self).filter_by(ativo=True).count()
    
    def __repr__(self):
        return f"{self.name} - Quantidade Disponível: {self.contar()}"
    