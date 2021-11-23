from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from app.config import Config


# Importa os componentes do Flask
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()

# Personaliza as mensagens de login
login_manager.login_view = 'usuarios.login'
login_manager.login_message_category = 'info'
login_manager.needs_refresh_message_category = 'info'
login_manager.login_message = 'É necessário realizar login para acessar\
                               essa página. Acesse a página "Sobre" para\
                               ver as contas de teste'
login_manager.needs_refresh_message = 'É necessário realizar login novamente.'


def create_app(config_class=Config):
    # Inicializa o Flask
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Importa as views
    from app.principal.views import principal
    from app.erros.handlers import erros
    from app.usuarios.views import usuarios
    from app.posts.views import posts
    from app.equipamentos.views import equipamentos
    from app.salas.views import salas
    from app.solicitacoes.views import solicitacoes

    # Registra os blueprints
    app.register_blueprint(principal, url_prefix='/')
    app.register_blueprint(erros, url_prefix='/erros')
    app.register_blueprint(usuarios, url_prefix='/usuarios')
    app.register_blueprint(posts, url_prefix='/posts')
    app.register_blueprint(equipamentos, url_prefix='/equipamentos')
    app.register_blueprint(salas, url_prefix='/salas')
    app.register_blueprint(solicitacoes, url_prefix='/solicitacoes')
    
    return app