from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin

from app import db, login_manager, fuso_horario


# Carrega o usuário que faz login da tabela apropriada
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) 

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    identificacao = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    imagem_perfil = db.Column(db.String(20), nullable=False, 
                              default='default.jpg')
    
    # Um usuário pode estar associado a múltiplas mensagens e solicitações
    posts = db.relationship('Post', backref='autor', lazy=True)
    solicitacoes = db.relationship('Solicitacao', backref='autor', lazy=True)
    relatorios = db.relationship('Relatorio', backref='autor', lazy=True)

    # Retorna o token necessário para que o usuário possa redefinir sua senha
    def obtem_token_redefinicao(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'usuario_id': self.id}).decode('utf-8')

    # Verifica se o token fornecido pelo usuário é válido
    @staticmethod
    def verifica_token_redefinicao(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            usuario_id = s.loads(token)['usuario_id']
        except:
            return None
        return Usuario.query.get(usuario_id)

    def __repr__(self):
        return f"{self.nome} ({self.identificacao})"

class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    data_postado = db.Column(db.DateTime, nullable=False, 
                             default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Uma mensagem tem somente um usuário como autor
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)

    def __repr__(self):
        return f"Post: {self.titulo} ({self.data_postado})"

# Tabelas que associam as solicitações aos equipamentos
solicitacao_e = db.Table('solicitacao_equipamento',
    db.Column('solicitacao_id', db.Integer, db.ForeignKey('solicitacoes.id'), 
              primary_key=True),
    db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamentos.id'), 
              primary_key=True)
)

class Solicitacao(db.Model):
    __tablename__ = 'solicitacoes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    turno = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Em Aberto')
    data_abertura = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_preferencial = db.Column(db.DateTime, nullable=True)
    data_entrega = db.Column(db.DateTime, nullable=True)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    data_cancelamento = db.Column(db.DateTime, nullable=True)
    data_finalizacao = db.Column(db.DateTime, nullable=True)
    qtd_equipamento = db.Column(db.Integer, nullable=True, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Uma solicitação está associada a um usuário e um tipo de equipamento
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), 
                           nullable=False)
    tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipos_equipamento.id'), 
                           nullable=True)

    # Uma solicitação está associada a múltiplos equipamentos ou uma sala
    equipamentos = db.relationship('Equipamento', secondary=solicitacao_e, 
                                   back_populates='solicitacoes')
    sala = db.relationship('Sala', back_populates='solicitacoes')
    tipo_eqp = db.relationship('TipoEquipamento', back_populates='solicitacoes')

    def __repr__(self):
        return f"Solicitacao #{self.id} - {self.tipo} - {self.status}"


class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.String(50), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Disponível')
    motivo_indisponibilidade = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um equipamento pertence a um tipo em específico
    tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipos_equipamento.id'), 
                            nullable=False)

    # Um equipamento faz parte de diferentes solicitações e relatórios
    tipo_eqp = db.relationship('TipoEquipamento', back_populates='equipamentos')
    solicitacoes = db.relationship('Solicitacao', secondary=solicitacao_e, 
                                   back_populates='equipamentos')
    relatorios = db.relationship('Relatorio', back_populates='equipamento')
   
    def __repr__(self):
        return f"{self.patrimonio} - {self.descricao}"


class TipoEquipamento(db.Model):
    __tablename__ = 'tipos_equipamento'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), unique=True, nullable=False)
    qtd_disponivel = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um tipo está associado a múltiplos equipamentos e solicitações
    equipamentos = db.relationship('Equipamento', back_populates='tipo_eqp')
    solicitacoes = db.relationship('Solicitacao', back_populates='tipo_eqp')

    def __repr__(self):
        return f"{self.nome} - Qtd. Disponível: {self.qtd_disponivel}"


class Sala(db.Model):
    __tablename__ = 'salas'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    setor = db.Column(db.String(20), nullable=False)
    qtd_aluno = db.Column(db.Integer, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, 
                       default='Disponível')
    motivo_indisponibilidade = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Uma sala faz parte de diferentes solicitações e relatórios
    solicitacoes = db.relationship('Solicitacao', back_populates='sala')
    relatorios = db.relationship('Relatorio', back_populates='sala')
    
    def __repr__(self):
        return f"{self.numero} - {self.setor} - Alunos: {self.qtd_aluno} - {self.status}"

class Relatorio(db.Model):
    __tablename__ = 'relatorios'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    manutencao = db.Column(db.Boolean, nullable=False, default=False)
    defeito = db.Column(db.Boolean, nullable=False, default=False)
    reforma = db.Column(db.Boolean, nullable=False, default=False)
    detalhes = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Aberto')
    data_abertura = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    data_finalizacao = db.Column(db.DateTime, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um relatório está associado a um usuário, e uma sala ou equipamento
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), 
                           nullable=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), 
                           nullable=True)

    equipamento = db.relationship('Equipamento', back_populates='relatorios')
    sala = db.relationship('Sala', back_populates='relatorios')

    def __repr__(self):
        return f"Relatório #{self.id} - {self.tipo} - {self.status}"