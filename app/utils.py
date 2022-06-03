import os
import secrets
from functools import wraps
from PIL import Image

from flask import url_for, current_app, flash, redirect
from flask_mail import Message
from flask_login import current_user

from app import mail

# Define um decorator para verificar se o usuário atual é um administrador
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.tipo.name == 'ADMIN':
            return f(*args, **kwargs)
        else:
            flash('Você não tem autorização para acessar esta página.', 'danger')
        return redirect(url_for('principal.inicio'))
    return wrap 

# Define um decorator para verificar se o usuário atual é um professor
def prof_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.tipo.name == 'PROF' or current_user.tipo.name == 'ADMIN':
            return f(*args, **kwargs)
        else:
            flash('Você não tem autorização para acessar esta página.', 'danger')
        return redirect(url_for('principal.inicio'))
    return wrap 

# Redimensiona e salva as imagens de perfil na pasta definida
def salva_imagem(form_picture):
    # Gera um nome aleatório pra imagem e define o diretório pra salvá-la
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/img_perfil', picture_fn)

    # Redimensiona e salva a imagem no caminho acima
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# Envia o email de redefinição de senha com o token gerado
def envia_email_redefinicao(usuario):
    token = usuario.obtem_token_redefinicao()
    msg = Message('UniGerência: Pedido de Redefinição de Senha',
                  sender='unigerencia.app@gmail.com',
                  recipients=[usuario.email])
    msg.body = f'''Para redefinir a sua senha, visite o seguinte link:
{url_for('usuarios.redefinir_token', token=token, _external=True)}

O link será válido por 30 minutos.
Se você não fez esse pedido, então apenas ignore este email e nenhuma alteração será feita.
'''
    mail.send(msg)

# Envia o email de aviso para um usuário com solicitações confirmadas
def envia_email_confirmacao(solicitacao):
    msg = Message('UniGerência: Aviso de Solicitação Confirmada',
                  sender='unigerencia.app@gmail.com',
                  recipients=[solicitacao.autor.email])
    msg.body = f'''Você possui uma solicitação confirmada:
{url_for('solicitacoes.solicitacao', solicitacao_id=solicitacao.id, _external=True)}
'''
    mail.send(msg)

# Envia o email de aviso para um usuário com solicitações com devolução atrasada
def envia_email_atraso(solicitacao):
    msg = Message('UniGerência: Aviso de Devolução Atrasada',
                  sender='unigerencia.app@gmail.com',
                  recipients=[solicitacao.autor.email])
    msg.body = f'''Você possui uma solicitação com devolução atrasada:
{url_for('solicitacoes.solicitacao', solicitacao_id=solicitacao.id, _external=True)}

Por favor, regularize sua situação assim que possível.
Se você já estiver regularizado, então apenas ignore este email.
'''
    mail.send(msg)
    