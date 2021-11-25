import os

# Define variáveis de ambiente importantes
class Config:
    # Chave criptográfica de sessão do Flask
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    # Variáveis do SQLAlchemy
    # Fornece acesso ao banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Variáveis do Mail
    # Permite o uso do serviço de email para enviar mensagens
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'deivyd.w@gmail.com'
    MAIL_PASSWORD = 'namrpxidjkpzlwrq'