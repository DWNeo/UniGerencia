from datetime import datetime

from flask_login import current_user

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
    
    # Recupera todas as mensagens presentes no banco de dados
    def recupera_tudo():
        return Post.query.filter_by(ativo=True).all()
    
    # Recupera o post pela ID e retorna erro 404 caso contrário
    def recupera_id(post_id):
        return Post.query.filter_by(id=post_id).filter_by(ativo=True).first_or_404()
        
    # Recupera as mensagens de um autor de forma paginada
    def recupera_autor_paginado(usuario, pagina, num):
        return Post.query.filter_by(autor=usuario).order_by(
            Post.data_postado.desc()).paginate(page=pagina, per_page=num)
    
    # Verifica se um usuário é o autor de uma mensagem (ou um admin)
    def verifica_autor(self, usuario):
        if self.autor == usuario or usuario.tipo.name == 'ADMIN':
            return True
        else:
            return False
            
    # Cria uma nova mensagem para ser inserida
    def cria(destinatario, form):
        return Post(titulo=form.titulo.data, 
                    destinatario=destinatario,
                    conteudo=form.conteudo.data,
                    autor=current_user)
        
    # Insere uma nova mensagem no banco de dados
    def insere(self):
        db.session.add(self)
        db.session.commit()
        
    # Atualiza uma mensagem existente no banco de dados
    def atualiza(self, form):
        self.titulo = form.titulo.data
        self.conteudo = form.conteudo.data
        self.data_atualizacao = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Desativa o registro de uma mensagem no banco de dados
    def exclui(self):
        self.ativo = False
        db.session.commit()
        
    def __repr__(self):
        return f"Post: {self.titulo} ({self.data_postado})"
    