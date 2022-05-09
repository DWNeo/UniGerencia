from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from whitenoise import WhiteNoise
from pytz import timezone

from app.config import Config

# Inicializa o Flask e seus componentes
app = Flask(__name__)
app.config.from_object(Config)
# Importa os componentes do Flask
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)

# Define a tela de login padrão
login_manager.login_view = 'usuarios.login'


# Define o fuso horário a ser considerado no datetime
# No caso desta aplicação é o horário de São Paulo (UTC-3)
fuso_horario = timezone('America/Sao_Paulo')

def create_app(config_class=Config):
    
    from app import models
    db.create_all()

    # Importa as views
    from app.principal.views import principal
    from app.erros.handlers import erros
    from app.usuarios.views import usuarios
    from app.posts.views import posts
    from app.equipamentos.views import equipamentos
    from app.salas.views import salas
    from app.solicitacoes.views import solicitacoes

    # Registra as blueprints
    app.register_blueprint(principal, url_prefix='/')
    app.register_blueprint(erros, url_prefix='/erros')
    app.register_blueprint(usuarios, url_prefix='/usuarios')
    app.register_blueprint(posts, url_prefix='/posts')
    app.register_blueprint(equipamentos, url_prefix='/equipamentos')
    app.register_blueprint(salas, url_prefix='/salas')
    app.register_blueprint(solicitacoes, url_prefix='/solicitacoes')

    # Importa o WhiteNoise
    # Permite que arquivos na pasta 'static' funcionem corretamente no Heroku
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/')
    
    return app
