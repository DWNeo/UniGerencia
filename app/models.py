from datetime import datetime
from email.policy import default
import enum

from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_login import UserMixin

from app import db, login_manager, fuso_horario


# Carrega o usuário que faz login da tabela apropriada
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) 

class TipoUsuario(enum.Enum):
    ALUNO = "Aluno"
    PROF = "Professor"
    ADMIN = "Administrador"
    
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    identificacao = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    tipo = db.Column(db.Enum(TipoUsuario), nullable=False)
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

class Status(enum.Enum):
    ABERTO = 'Aberto'
    SOLICITADO = 'Solicitado' 
    CONFIRMADO = 'Confirmado'
    EMUSO = 'Em Uso'
    FECHADO = 'Fechado'
    CANCELADO = 'Cancelado'
    PENDENTE = 'Pendente'
    EMMANUTENCAO = 'Em Manutencao'
    DESABILITADO = 'Desabilitado'

class Turno(db.Model):
    __tablename__ = 'turnos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    data_inicio = db.Column(db.Time, nullable=False)
    data_fim = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    solicitacoes = db.relationship('Solicitacao', back_populates='turno')
    def __repr__(self):
        return f"{self.name} - Hora Inicio: {self.data_inicio} - Hora Fim: {self.data_fim}"

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

    turno = db.relationship('Turno', back_populates='solicitacoes')
    # Uma solicitação está associada a um usuário e um tipo de equipamento
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos.id'), 
                           nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'solicitacoes',
        'polymorphic_on': tipo
    }

    def __repr__(self):
        return f"Solicitação #{self.id} - {self.tipo} - {self.status}"
 

# Tabelas que associam as solicitações as salas
solicitacao_s = db.Table('solicitacao_s',
    db.Column('solicitacao_sala_id', db.Integer, db.ForeignKey('solicitacoes_salas.id'), 
              primary_key=True),
    db.Column('sala_id', db.Integer, db.ForeignKey('salas.id'), 
              primary_key=True)
)

class SolicitacaoSala(Solicitacao):
    __tablename__ = 'solicitacoes_salas'
    
    id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), primary_key=True)

    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    setor = db.relationship('Setor', back_populates='solicitacoes')
    # Uma solicitação está associada a múltiplos equipamentos ou uma sala
    salas = db.relationship('Sala', secondary= solicitacao_s, 
                                    back_populates='solicitacoes')
    __mapper_args__ = {
        'polymorphic_identity': 'solicitacoes_salas',
    }

class Setor(db.Model):
    __tablename__ = 'setores'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    qtd_disponivel = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)


    solicitacoes = db.relationship('SolicitacaoSala', back_populates='setor')    
    salas = db.relationship('Sala', back_populates='setor')
    def __repr__(self):
        return f"{self.name} - Quantidade Disponível: {self.qtd_disponivel}"

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
    

    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    # Uma sala faz parte de diferentes solicitações e relatórios
    solicitacoes = db.relationship('SolicitacaoSala', secondary=solicitacao_s, 
                                   back_populates='salas')
    relatorios = db.relationship('RelatorioSala', back_populates='sala')
    setor = db.relationship('Setor', back_populates='salas')  

    def __repr__(self):
        return f"{self.numero} - {self.setor.name} - Alunos: {self.qtd_aluno} - {self.status.value}"

# Tabelas que associam as solicitações aos equipamentos
solicitacao_e = db.Table('solicitacao_e',
    db.Column('solicitacao_equipamento_id', db.Integer, db.ForeignKey('solicitacoes_equipamentos.id'), 
              primary_key=True),
    db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamentos.id'), 
              primary_key=True)
)

class SolicitacaoEquipamento(Solicitacao):
    __tablename__ = 'solicitacoes_equipamentos'
    
    id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), primary_key=True)

    tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipos_equipamento.id'), 
                           nullable=True)
    # Tabelas que associam as solicitações aos equipamentos
    equipamentos = db.relationship('Equipamento', secondary=solicitacao_e, 
                                   back_populates='solicitacoes')
    tipo_eqp = db.relationship('TipoEquipamento', back_populates='solicitacoes')

    __mapper_args__ = {
        'polymorphic_identity': 'solicitacoes_equipamentos'
    }



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

    def __repr__(self):
        return f"{self.nome} - Qtd. Disponível: {self.qtd_disponivel}"

class TipoRelatorio(enum.Enum):
    REVISAO = "Revisão"
    MANUTENCAO = "Manutenção"
    OUTRO = "Outro"

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


class RelatorioEquipamento(Relatorio):
    __tablename__ = 'relatorios_equipamento'
    
    id = db.Column(db.Integer, db.ForeignKey('relatorios.id'), primary_key=True)
    defeito = db.Column(db.Boolean, nullable=False, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'relatorios_equipamento'
    }
    # Um relatório está associado a um equipamento
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), 
                           nullable=True)

    equipamento = db.relationship('Equipamento', back_populates='relatorios')

    def __repr__(self):
        return f"Relatório #{self.id} - {self.tipo} - {self.status}"