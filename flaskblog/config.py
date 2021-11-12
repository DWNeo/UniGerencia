import os


class Config:
    #SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    #MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_USERNAME = 'deivyd.w@gmail.com'
    #MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_PASSWORD = 'Deivyd10226578!'
