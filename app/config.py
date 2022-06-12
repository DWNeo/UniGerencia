# Define variáveis de ambiente (DESENVOLVIMENTO)
class Config:
    # Controla o modo debug
    DEBUG = True
    # Chave criptográfica de sessão do Flask
    SECRET_KEY = 'aj5mUuYnFw3Gy/bL2TYpCXjQGRGbuEgq6I5gBE1ZXjI='
    SALT = 'UniGerência'
    # Tempo para expirar os tokens (1800 = 30 minutos)
    MAX_AGE = 1800 
    # Ativa o Scheduler
    SCHEDULER_API_ENABLED = True
    # Define o servidor em que o app está rodando
    SERVER_NAME = 'localhost:5000'
    SCHEME = 'http'
    # Variáveis do SQLAlchemy
    # Configura acesso ao banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///storage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Variáveis do Mail
    # Configura o uso do serviço de email para enviar mensagens
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'unigerencia.app@gmail.com'
    MAIL_PASSWORD = 'qjsnhwzykzkjfsjj'

# Define variáveis de ambiente (PRODUÇÃO)
class ConfigProd:
    # Controla o modo debug
    DEBUG = False
    # Chave criptográfica de sessão do Flask
    SECRET_KEY = 'aj5mUuYnFw3Gy/bL2TYpCXjQGRGbuEgq6I5gBE1ZXjI='
    SALT = 'UniGerência'
    # Tempo para expirar os tokens (1800 = 30 minutos)
    MAX_AGE = 1800 
    # Ativa o Scheduler
    SCHEDULER_API_ENABLED = True
    # Define o servidor em que o app está rodando
    SERVER_NAME = 'unigerencia.herokuapp.com'
    SCHEME = 'https'
    # Variáveis do SQLAlchemy
    # Configura acesso ao banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///storage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Variáveis do Mail
    # Configura o uso do serviço de email para enviar mensagens
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'unigerencia.app@gmail.com'
    MAIL_PASSWORD = 'qjsnhwzykzkjfsjj'
    