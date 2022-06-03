from datetime import datetime
import enum

from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, current_user, login_user

from app import db, bcrypt, login_manager, fuso_horario
from app.utils import salva_imagem

# Carrega o usuário que faz login da tabela apropriada
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) 

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

    # Retorna o token necessário para que o usuário possa redefinir sua senha
    def obtem_token_redefinicao(self):
        s = Serializer(current_app.config['SECRET_KEY'], current_app.config['SALT'])
        return s.dumps({'usuario_id': self.id})

    # Verifica se o token fornecido pelo usuário é válido
    @staticmethod
    def verifica_token_redefinicao(token):
        s = Serializer(current_app.config['SECRET_KEY'], current_app.config['SALT'])
        try:
            usuario_id = s.loads(token, max_age=current_app.config['MAX_AGE'],)['usuario_id']
        except:
            return None
        return Usuario.query.get(usuario_id)
    
    # Recupera todos os usuários inseridos no banco de dados
    def recupera_todos():
        return Usuario.query.filter_by(ativo=True).all()
    
    # Recupera o usuário pela ID e retorna erro 404 caso contrário
    def recupera_id(usuario_id):
        return Usuario.query.filter_by(id=usuario_id).filter_by(ativo=True).first_or_404()
    
    # Recupera o usuário pelo Email
    def recupera_email(usuario_email):
        return Usuario.query.filter_by(email=usuario_email).filter_by(ativo=True).first()
    
    # Verifica a senha inserida e realiza login do usuário
    def login(usuario, form):
        if usuario and bcrypt.check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario, remember=form.lembrar.data)
            return True
        else:
            return False
    
    # Insere um novo usuário no banco de dados (Tela de Registro)
    def registra(form):
        # Gera o hash da senha do novo usuário
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        
        # Insere novo usuário no banco de dados
        usuario = Usuario(nome=form.nome.data, 
                          identificacao=form.identificacao.data,
                          email=form.email.data, 
                          senha=hash_senha,
                          tipo=form.tipo.data)
        db.session.add(usuario)
        db.session.commit()
    
    # Insere um novo usuário no banco de dados (Admin)
    def insere(form):
        # Realiza o tratamento da imagem de perfil enviada
        if form.imagem.data:
            arquivo_imagem = salva_imagem(form.imagem.data)
            imagem_perfil = arquivo_imagem
        else:
            imagem_perfil = None
        
        # Insere novo usuário no banco de dados
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        usuario = Usuario(nome=form.nome.data, 
                          identificacao=form.identificacao.data,
                          email=form.email.data, 
                          senha=hash_senha,
                          imagem_perfil=imagem_perfil, 
                          tipo=form.tipo.data)
        db.session.add(usuario)
        db.session.commit()
    
    # Atualiza o perfil do usuário atual no banco de dados
    def perfil(form):
        # Realiza o tratamento da imagem enviada
        if form.imagem.data:
            arquivo_imagem = salva_imagem(form.imagem.data)
            current_user.imagem_perfil = arquivo_imagem
            
        # Atualiza dados do usuário no banco de dados  
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        current_user.senha = hash_senha
        current_user.nome = form.nome.data
        current_user.identificacao = form.identificacao.data
        current_user.email = form.email.data
        current_user.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
    
    # Atualiza um usuário existente específico no banco de dados
    def atualiza(usuario, form):
        # Realiza o tratamento da imagem enviada
        if form.imagem.data:
            arquivo_imagem = salva_imagem(form.imagem.data)
            usuario.imagem_perfil = arquivo_imagem
            
        # Atualiza dados do usuário no banco de dados  
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        usuario.senha = hash_senha
        usuario.nome = form.nome.data
        usuario.tipo = form.tipo.data
        usuario.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
       
    # Redefine a senha de um usuário existente
    def nova_senha(usuario, form):
        # Gera um novo hash com base na nova senha
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        usuario.senha = hash_senha
        usuario.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
    
    # Desativa o registro de um usuário no banco de dados
    def exclui(usuario):
        usuario.ativo = False
        db.session.commit()

    def __repr__(self):
        return f"{self.nome} ({self.identificacao})"
    