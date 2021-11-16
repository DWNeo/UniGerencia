from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.String(50), nullable=False)
    tipo_eqp = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Disponível')
    #req_id = db.relationship('Requisicao', backref='eqp_req', lazy=True)
    #sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    #tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipo_eqp.id'), nullable=False)

    def __repr__(self):
        return f"Equipamento('{self.patrimonio}', '{self.descricao}', '{self.data_cadastro}', '{self.status}', '{self.tipo_eqp}')"

class Sala(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    setor = db.Column(db.String(20), nullable=False)
    qtd_aluno = db.Column(db.Integer, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Disponível')
    #req_id = db.relationship('Requisicao', backref='sala_req', lazy=True)

    def __repr__(self):
        return f"Sala('{self.numero}', '{self.setor}', '{self.qtd_aluno}', '{self.data_cadastro}', '{self.status}')"

'''
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    identificacao = db.Column(db.String(20), unique=True, nullable=False)
    img_perfil = db.Column(db.String(20), nullable=False, default='default.jpg')
    admin = db.Column(db.Boolean, nullable=False, default=False)
    #requisicoes = db.relationship('Requisicao', backref='usuario', lazy=True)
    #posts = db.relationship('Post', backref='author', lazy=True)

    def obter_token_redefinicao(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'id_usuario': self.id}).decode('utf-8')

    @staticmethod
    def verificar_token_redefinicao(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            id_usuario = s.loads(token)['id_usuario']
        except:
            return None
        return Usuario.query.get(id_usuario)

    def __repr__(self):
        return f"Usuario('{self.usuario}', '{self.email}', '{self.img_perfil}')"
'''