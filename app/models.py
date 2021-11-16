from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Usuario(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    identification = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    
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
        return Usuario.query.get(user_id)

    def __repr__(self):
        return f"Usuario('{self.name}', '{self.identification}', {self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ativo = db.Column(db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Equipamento(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.String(50), nullable=False)
    tipo_eqp = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Disponível')
    ativo = db.Column(db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return f"Equipamento('{self.patrimonio}', '{self.descricao}', '{self.data_cadastro}', '{self.status}', '{self.tipo_eqp}')"

class Sala(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    setor = db.Column(db.String(20), nullable=False)
    qtd_aluno = db.Column(db.Integer, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Disponível')
    ativo = db.Column(db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return f"Sala('{self.numero}', '{self.setor}', '{self.qtd_aluno}', '{self.data_cadastro}', '{self.status}')"