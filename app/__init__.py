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

# Customiza o processo de login
login_manager.login_view = 'usuarios.login'
login_manager.login_message_category = 'info'
login_manager.needs_refresh_message_category = 'info'
login_manager.login_message = 'É necessário realizar login para acessar essa página.'
login_manager.needs_refresh_message = 'É necessário realizar login novamente.'

def create_app(config_class=Config):
	# Inicializa o Flask
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)

	# Importa as rotas
	from app.principal.routes import principal
	from app.usuarios.routes import usuarios
	from app.posts.routes import posts
	from app.erros.handlers import erros
	from app.equipamentos.routes import equipamentos
	from app.salas.routes import salas

	# Registra os blueprints
	app.register_blueprint(principal)
	app.register_blueprint(usuarios)
	app.register_blueprint(posts)
	app.register_blueprint(erros)
	app.register_blueprint(equipamentos)
	app.register_blueprint(salas)
	
	return app