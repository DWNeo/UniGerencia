from datetime import datetime

from app import db, fuso_horario

# Classe para mensagens enviadas pelos usuários
class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    data_postado = db.Column(db.DateTime, nullable=False, 
                             default=datetime.now().astimezone(fuso_horario))
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Uma mensagem tem somente um usuário como autor e um destinatário
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                                nullable=True)
    
    # Recupera as mensagens de um autor de forma paginada
    def recupera_autor_paginado(usuario, pagina, num):
        return Post.query.filter_by(autor=usuario).order_by(
            Post.data_postado.desc()).paginate(page=pagina, per_page=num)

    def __repr__(self):
        return f"Post: {self.titulo} ({self.data_postado})"
    