import os
import secrets
from PIL import Image

from flask import url_for, current_app
from flask_mail import Message

from app import mail

# Envia o email de redefinição de senha com o token gerado
def enviar_email_redefinicao(usuario):
    token = usuario.obter_token_redefinicao()
    msg = Message('UniGerência: Pedido de Redefinição de Senha',
                  sender='UniGerência',
                  recipients=[usuario.email])
    msg.body = f'''Para redefinir a sua senha, visite o seguinte link:
{url_for('usuarios.redefinir_token', token=token, _external=True, 
         _scheme=current_app.config['SCHEME'])}

O link será válido por 30 minutos.
Se você não fez esse pedido, então apenas ignore este email e nenhuma alteração será feita.
'''
    mail.send(msg)

# Envia o email de aviso para um usuário com solicitações confirmadas
def enviar_email_confirmacao(solicitacao):
    msg = Message('UniGerência: Aviso de Solicitação Confirmada',
                  sender='UniGerência',
                  recipients=[solicitacao.autor.email])
    msg.body = f'''Você possui uma solicitação confirmada:
{url_for('solicitacoes.solicitacao', solicitacao_id=solicitacao.id, _external=True, 
         _scheme=current_app.config['SCHEME'])}
'''
    mail.send(msg)

# Envia o email de aviso para um usuário com solicitações com devolução atrasada
def enviar_email_atraso(solicitacao):
    msg = Message('UniGerência: Aviso de Devolução Atrasada',
                  sender='UniGerência',
                  recipients=[solicitacao.autor.email])
    msg.body = f'''Você possui uma solicitação com devolução atrasada:
{url_for('solicitacoes.solicitacao', solicitacao_id=solicitacao.id, _external=True, 
         _scheme=current_app.config['SCHEME'])}

Por favor, regularize sua situação assim que possível.
Se você já estiver regularizado, então apenas ignore este email.
'''
    mail.send(msg)
    
# Envia um email de aviso para um usuário com uma nova mensagem recebida
def enviar_email_mensagem(post):
    msg = Message('UniGerência: Nova Mensagem Recebida',
                  sender='UniGerência',
                  recipients=[post.destinatario.email])
    msg.body = f'''Você recebeu uma nova mensagem:
{url_for('posts.post', post_id=post.id, _external=True, 
         _scheme=current_app.config['SCHEME'])}
'''
    mail.send(msg)