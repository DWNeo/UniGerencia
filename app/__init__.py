from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from app.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.needs_refresh_message_category = 'info'
login_manager.login_message = 'É necessário realizar login para acessar essa página.'
login_manager.needs_refresh_message = 'É necessário realizar login novamente.'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.principal.routes import principal
    from app.users.routes import users
    from app.posts.routes import posts
    from app.erros.handlers import erros
    from app.equipamentos.routes import equipamentos
    from app.salas.routes import salas
    #from app.usuarios.routes import usuarios
    app.register_blueprint(principal)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(erros)
    app.register_blueprint(equipamentos)
    app.register_blueprint(salas)
    #app.register_blueprint(usuarios)
    
    return app
