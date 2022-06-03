# Define variáveis de ambiente importantes
class Config:
    # Chave criptográfica de sessão do Flask
    SECRET_KEY = 'aj5mUuYnFw3Gy/bL2TYpCXjQGRGbuEgq6I5gBE1ZXjI='
    SALT = 'UniGerência'
    
    # Tempo para expirar os tokens (1800 = 30 minutos)
    MAX_AGE = 1800 

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
    