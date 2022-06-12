from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_apscheduler import APScheduler
from whitenoise import WhiteNoise
from pytz import timezone

from app.config import ConfigDev, ConfigProd

# Importa os componentes do Flask
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()
scheduler = APScheduler()

# Define a tela de login padrão
login_manager.login_view = 'usuarios.login'

# Define o fuso horário a ser considerado no datetime
# No caso desta aplicação é o horário de São Paulo (UTC-3)
fuso_horario = timezone('America/Sao_Paulo')

def create_app():
    # Inicializa o Flask e seus componentes
    app = Flask(__name__)
    app.config.from_object(ConfigDev)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    scheduler.start()
    
    # Importa os controllers
    from app.controllers.principal import principal
    from app.controllers.erros import erros
    from app.controllers.usuarios import usuarios
    from app.controllers.posts import posts
    from app.controllers.equipamentos import equipamentos
    from app.controllers.salas import salas
    from app.controllers.solicitacoes import solicitacoes
    
    # Registra as blueprints
    app.register_blueprint(principal, url_prefix='/')
    app.register_blueprint(erros, url_prefix='/erros')
    app.register_blueprint(usuarios, url_prefix='/usuarios')
    app.register_blueprint(posts, url_prefix='/posts')
    app.register_blueprint(equipamentos, url_prefix='/equipamentos')
    app.register_blueprint(salas, url_prefix='/salas')
    app.register_blueprint(solicitacoes, url_prefix='/solicitacoes')

    # Importa o WhiteNoise
    # Permite que arquivos na pasta 'static' sejam servidos corretamente
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/', prefix='assets/')

    return app
