from datetime import datetime
import enum
from functools import wraps

from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app, flash, redirect, url_for
from flask_login import UserMixin, current_user, login_user

from app import db, bcrypt, login_manager, fuso_horario
from app.utils import salvar_imagem

# Carrega o usuário que faz login da tabela apropriada
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) 

# Define um decorator para verificar se o usuário atual é um administrador
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if Usuario.verificar_admin(current_user):
            return f(*args, **kwargs)
        else:
            flash('Você não tem autorização para acessar esta página.', 'danger')
        return redirect(url_for('principal.inicio'))
    return wrap 

# Define um decorator para verificar se o usuário atual é um professor
def prof_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if Usuario.verificar_prof(current_user):
            return f(*args, **kwargs)
        else:
            flash('Você não tem autorização para acessar esta página.', 'danger')
        return redirect(url_for('principal.inicio'))
    return wrap 

# Classe enum para os tipos de usuários do sistema
class TipoUsuario(enum.Enum):
    ALUNO = "Aluno"
    PROF = "Professor"
    ADMIN = "Administrador"
    
# Classe para os usuários do sistema
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
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    tipo = db.Column(db.Enum(TipoUsuario), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    imagem_perfil = db.Column(db.String(20), nullable=False, 
                              default='default.jpg')
    
    # Um usuário pode estar associado a múltiplas mensagens e solicitações
    posts = db.relationship('Post', backref='autor', 
                            foreign_keys='Post.usuario_id', lazy=True)
    recipiente = db.relationship('Post', backref='destinatario', 
                                 foreign_keys='Post.destinatario_id', lazy=True)
    solicitacoes = db.relationship('Solicitacao', backref='autor', lazy=True)
    relatorios = db.relationship('Relatorio', backref='autor', lazy=True)

    def __repr__(self):
        return f"{self.nome} ({self.identificacao})"

    # Retorna o token necessário para que o usuário possa redefinir sua senha
    def obter_token_redefinicao(self):
        s = Serializer(current_app.config['SECRET_KEY'], current_app.config['SALT'])
        return s.dumps({'usuario_id': self.id})

    # Verifica se o token fornecido pelo usuário é válido
    @staticmethod
    def verificar_token_redefinicao(token):
        s = Serializer(current_app.config['SECRET_KEY'], current_app.config['SALT'])
        try:
            usuario_id = s.loads(token, max_age=current_app.config['MAX_AGE'],)['usuario_id']
        except:
            return None
        return Usuario.query.get(usuario_id)
    
    # Recupera todos os usuários presentes no banco de dados
    def recuperar_tudo():
        return Usuario.query.filter_by(ativo=True).all()
    
    # Recupera o usuário pela ID e retorna erro 404 caso contrário
    def recuperar_id(usuario_id):
        return Usuario.query.filter_by(id=usuario_id).filter_by(ativo=True).first_or_404()
    
    # Recupera o usuário pelo Identificação
    def recuperar_identificacao(usuario_idf):
        return Usuario.query.filter_by(identificacao=usuario_idf).filter_by(ativo=True).first()
    
    # Recupera o usuário pelo Email
    def recuperar_email(usuario_email):
        return Usuario.query.filter_by(email=usuario_email).filter_by(ativo=True).first()
    
    # Verifica se um usuário é administrador ou não
    def verificar_admin(self):
        if self.tipo.name == 'ADMIN':
            return True
        else:
            return False
        
    # Verifica se um usuário é prof ou administrador
    def verificar_prof(self):
        if self.tipo.name == 'PROF' or self.tipo.name == 'ADMIN':
            return True
        else:
            return False
        
    # Verifica a senha inserida e realiza login do usuário
    def login(self, form):
        if self and bcrypt.check_password_hash(self.senha, form.senha.data):
            login_user(self, remember=form.lembrar.data)
            return True
        else:
            return False
    
    # Cria um novo usuário para ser inserido
    def criar(form):
        # Realiza o tratamento da imagem de perfil enviada
        if form.imagem.data:
            arquivo_imagem = salvar_imagem(form.imagem.data)
            imagem_perfil = arquivo_imagem
        else:
            imagem_perfil = None 
        # Gera o hash da senha do novo usuário
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        # Cria um usuário conforme dados recebidos do formulário
        return Usuario(nome=form.nome.data, 
                       identificacao=form.identificacao.data,
                       email=form.email.data, 
                       senha=hash_senha,
                       imagem_perfil=imagem_perfil,
                       tipo=form.tipo.data)
        
    # Insere um novo usuário no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
    
    # Atualiza um usuário existente no banco de dados
    def atualizar(self, form):
        # Realiza o tratamento da imagem enviada
        if form.imagem.data:
            arquivo_imagem = salvar_imagem(form.imagem.data)
            self.imagem_perfil = arquivo_imagem
        # Atualiza o tipo de usuário, se for necessário
        try:
            self.tipo = form.tipo.data
        except:
            print(self.tipo)
        # Atualiza dados do usuário no banco de dados  
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        self.senha = hash_senha
        self.nome = form.nome.data
        self.identificacao = form.identificacao.data
        self.email = form.email.data
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
       
    # Redefine a senha de um usuário existente
    def nova_senha(self, senha):
        # Gera um novo hash com base na nova senha
        hash_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
        self.senha = hash_senha
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
    
    # Desativa o registro de um usuário no banco de dados
    def excluir(self):
        self.ativo = False
        db.session.commit()
    