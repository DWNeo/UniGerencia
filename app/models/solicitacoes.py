from datetime import datetime
import time

from flask_login import current_user

from app import db, fuso_horario
from app.models.status import Status

# Classe para as solicitações de equipamentos e salas
class Solicitacao(db.Model):
    __tablename__ = 'solicitacoes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status), default=Status.ABERTO.name)
    data_abertura = db.Column(db.DateTime, nullable=False, 
                              default=datetime.now().astimezone(fuso_horario))
    data_inicio_pref = db.Column(db.Date, nullable=False)
    data_fim_pref = db.Column(db.Date, nullable=False)
    data_retirada = db.Column(db.DateTime, nullable=True)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    data_cancelamento = db.Column(db.DateTime, nullable=True)
    data_finalizacao = db.Column(db.DateTime, nullable=True)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    descricao = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Uma solicitação está associada a um usuário e um turno
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), 
                           nullable=False)
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos.id'), 
                           nullable=False)
    
    turno = db.relationship('Turno', back_populates='solicitacoes')

    __mapper_args__ = {
        'polymorphic_identity': 'SOLICITACAO',
        'polymorphic_on': tipo
    }
    
    def __repr__(self):
        return f"Solicitação #{self.id} - {self.tipo} - {self.status.value}"
    
    # Recupera todas as solicitações presentes no banco de dados
    def recuperar_tudo():
        return Solicitacao.query.filter_by(ativo=True).all()
    
    # Recupera todas as solicitações de um autor
    def recuperar_tudo_autor(usuario):
        return Solicitacao.query.filter_by(autor=usuario).filter_by(ativo=True).all()
    
    # Recupera a solicitação pela ID e retorna erro 404 caso contrário
    def recuperar_id(sol_id):
        return Solicitacao.query.filter_by(id=sol_id).filter_by(ativo=True).first_or_404()
    
    # Recupera todas as solicitações em aberto no banco de dados
    def recuperar_aberto():
        return Solicitacao.query.filter_by(status='ABERTO').filter_by(ativo=True).all()
    
    # Recupera todas as solicitações em uso no banco de dados
    def recuperar_em_uso():
        return Solicitacao.query.filter_by(status='EMUSO').filter_by(ativo=True).all()
    
    # Recupera todas as solicitações pendentes de um usuário
    def recuperar_pendente_autor(usuario):
        return Solicitacao.query.filter_by(status='PENDENTE').filter_by(
            autor=usuario).filter_by(ativo=True).all()
        
    # Recupera as últimas solicitações de um usuário específico
    def recuperar_ultimas_autor(usuario, limite):
        return Solicitacao.query.filter_by(autor=usuario).filter_by(
            ativo=True).order_by(Solicitacao.id.desc()).limit(limite)
     
    # Recupera as últimas solicitações de um equipamento específico
    def recuperar_ultimas_eqp(equipamento, limite):
        return Solicitacao.query.filter(
            SolicitacaoEquipamento.equipamentos.contains(equipamento)).filter_by(
            ativo=True).order_by(SolicitacaoEquipamento.id.desc()).limit(limite)
        
    # Recupera as mensagens de um autor de forma paginada
    def recuperar_ultimas_sala(sala, limite):
        return Solicitacao.query.filter(
            SolicitacaoSala.salas.contains(sala)).filter_by(
            ativo=True).order_by(SolicitacaoSala.id.desc()).limit(limite)
    
    # Retorna o tempo restante para a solicitação entrar em atraso
    def tempo_restante(self):
        if(self.data_devolucao and self.status.name == 'EMUSO'):
            agora = datetime.now().astimezone(fuso_horario)
            tempo_restante = int(datetime.timestamp(self.data_devolucao) - 
                                  datetime.timestamp(agora))
            if tempo_restante <= 0:
                return None
            minutos, segundos = divmod(tempo_restante, 60)
            horas, minutos = divmod(minutos, 60)
            return "%02d:%02d:%02d" % (horas, minutos, segundos)
        else:
            return None

    def verificar_inicio_hoje(data_inicio_pref):
        if data_inicio_pref == datetime.now().astimezone(fuso_horario).date():
            return True
        else:
            return False

    def verificar_autor(self, usuario):
        if self.autor == usuario or usuario.tipo.name == 'ADMIN':
            return True
        else:
            return False
        
    def verificar_aberto(self):
        if self.status.name == 'ABERTO' or self.status.name == 'SOLICITADO':
            return True
        else:
            return False
        
    def verificar_confirmado(self):
        if self.status.name == 'CONFIRMADO':
            return True
        else:
            return False
        
    def verificar_em_uso(self):
        if self.status.name == 'EMUSO':
            return True
        else:
            return False
        
    def verificar_pendente(self):
        if self.status.name == 'PENDENTE':
            return True
        else:
            return False
    
    def verificar_atraso(self):
        if (datetime.now().astimezone(fuso_horario) > 
            self.data_devolucao.astimezone(fuso_horario)):
            return True
        else:
            return False
        
    # Insere a solicitação no banco de dados
    def inserir(self):
        db.session.add(self)
        db.session.commit()
        return
    
    # Atualiza o status de um solicitação para 'Solicitado'
    def solicitado(self):
        self.status = 'SOLICITADO'    
        db.session.commit() 
    
    # Atualiza o status de um solicitação para 'Confirmado'
    def confirmar(self, lista_itens):
        self.status = 'CONFIRMADO'
        if self.tipo == 'EQUIPAMENTO':
            self.equipamentos = lista_itens
            for equipamento in self.equipamentos:
                equipamento.status = 'CONFIRMADO'
        if self.tipo == 'SALA':
            self.salas = lista_itens
            for sala in self.salas:
                sala.status = 'CONFIRMADO'     
        db.session.commit()  
        
    # Atualiza o status de um solicitação para 'Em Uso'
    def em_uso(self, form):
        self.status = 'EMUSO'
        self.data_retirada = datetime.now().astimezone(fuso_horario)
        # Combina data de devolução com o horário final do turno
        self.data_devolucao = datetime.combine(form.data_devolucao.data, 
                                               self.turno.hora_fim)
        if self.tipo == 'EQUIPAMENTO':
            for equipamento in self.equipamentos:
                equipamento.status = 'EMUSO'
        if self.tipo == 'SALA':
            for sala in self.salas: 
                sala.status = 'EMUSO'
        db.session.commit()
    
    # Atualiza o status de um solicitação para 'Pendente'
    def pendente(self):
        self.status = 'PENDENTE'
        if self.tipo == 'EQUIPAMENTO':
            for equipamento in self.equipamentos:
                equipamento.status = 'PENDENTE'
        if self.tipo == 'SALA':
            for sala in self.salas:
                sala.status = 'PENDENTE'     
        db.session.commit()
       
    # Atualiza o status de um solicitação para 'Finalizado' 
    def finalizar(self):
        self.status = 'FECHADO'
        self.data_finalizacao = datetime.now().astimezone(fuso_horario)
        if self.tipo == 'EQUIPAMENTO':
            for equipamento in self.equipamentos:
                equipamento.status = 'ABERTO'
        if self.tipo == 'SALA':
            for sala in self.salas:
                sala.status = 'ABERTO'
        db.session.commit()
       
    # Atualiza o status de um solicitação para 'Cancelado' 
    def cancelar(self):
        if self.status != 'ABERTO' and self.status != 'SOLICITADO':
            if self.tipo == 'EQUIPAMENTO':
                if self.equipamentos:
                    for equipamento in self.equipamentos:
                        equipamento.status = 'ABERTO'
            if self.tipo == 'SALA':
                if self.salas:
                    for sala in self.salas:
                        sala.status = 'ABERTO' 
        self.status = 'CANCELADO'
        self.data_cancelamento = datetime.now().astimezone(fuso_horario)
        db.session.commit()
        
    # Desativa o registro de uma solicitação no banco de dados
    def excluir(self):
        # Atualiza o status de equipamentos e salas antes de exluir a solicitação
        if self.status.name == 'CONFIRMADO':
            if self.equipamentos:
                for equipamento in self.equipamentos:
                    equipamento.status = 'ABERTO'
            if self.salas:
                for sala in self.salas:
                    sala.status = 'ABERTO'
        self.status = 'FECHADO'
        self.ativo = False
        db.session.commit()
 
# Tabela que associa as solicitações às salas
solicitacao_s = db.Table('solicitacao_s',
    db.Column('solicitacao_sala_id', db.Integer, db.ForeignKey('solicitacoes_salas.id'), 
              primary_key=True),
    db.Column('sala_id', db.Integer, db.ForeignKey('salas.id'), 
              primary_key=True)
)

# Tabela que associam as solicitações aos equipamentos
solicitacao_e = db.Table('solicitacao_e',
    db.Column('solicitacao_equipamento_id', db.Integer, db.ForeignKey('solicitacoes_equipamentos.id'), 
              primary_key=True),
    db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamentos.id'), 
              primary_key=True)
)

# Classe específica para as solicitações de salas
class SolicitacaoSala(Solicitacao):
    __tablename__ = 'solicitacoes_salas'
    
    id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), primary_key=True)

    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    
    # Pode estar associada a múltiplas salas de um único setor
    setor = db.relationship('Setor', back_populates='solicitacoes')
    salas = db.relationship('Sala', secondary= solicitacao_s, 
                                    back_populates='solicitacoes')
    
    __mapper_args__ = {
        'polymorphic_identity': 'SALA',
    }
    
    # Verifica se o usuário já possui uma solicitação não finalizada
    def verificar_existente_usuario(usuario):
        solicitacao = SolicitacaoSala.query.filter_by(autor=usuario).filter_by(
                      ativo=True).order_by(SolicitacaoSala.id.desc()).first()
        if solicitacao:
            if (solicitacao.status.name != 'CANCELADO' and 
                solicitacao.status.name != 'FECHADO'):
                return True
        return False
    
    # Cria uma nova solitação de equipamento para ser inserida
    def criar(status, form):
        return SolicitacaoSala(turno_id=form.turno.data,
                               usuario_id=current_user.id,
                               descricao=form.descricao.data,
                               quantidade=form.qtd_preferencia.data,
                               setor_id=form.setor.data,
                               data_inicio_pref=form.data_inicio_pref.data,
                               data_fim_pref=form.data_fim_pref.data,
                               status=status)
    
    def inserir(self):
        return super().inserir()
    

# Classe específica para as solicitações de equipamentos
class SolicitacaoEquipamento(Solicitacao):
    __tablename__ = 'solicitacoes_equipamentos'
    
    id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), primary_key=True)

    tipo_eqp_id = db.Column(db.Integer, db.ForeignKey('tipos_equipamento.id'), 
                           nullable=True)
    
    # Pode estar associada a múltiplos equipamentos de um único tipo
    equipamentos = db.relationship('Equipamento', secondary=solicitacao_e, 
                                   back_populates='solicitacoes')
    tipo_eqp = db.relationship('TipoEquipamento', back_populates='solicitacoes')

    __mapper_args__ = {
        'polymorphic_identity': 'EQUIPAMENTO'
    }
    
    # Verifica se o usuário já possui uma solicitação não finalizada
    def verificar_existente_usuario(usuario):
        solicitacao = SolicitacaoEquipamento.query.filter_by(autor=usuario).filter_by(
                      ativo=True).order_by(SolicitacaoEquipamento.id.desc()).first()
        if solicitacao:
            if (solicitacao.status.name != 'CANCELADO' and 
                solicitacao.status.name != 'FECHADO'):
                return True
        return False
        
    # Cria uma nova solitação de sala para ser inserida
    def criar(status, form):
        return SolicitacaoEquipamento(tipo_eqp_id=form.tipo_equipamento.data,
                                      turno_id=form.turno.data,
                                      usuario_id=current_user.id,
                                      descricao=form.descricao.data,
                                      quantidade=form.qtd_preferencia.data,
                                      data_inicio_pref=form.data_inicio_pref.data,
                                      data_fim_pref=form.data_fim_pref.data,
                                      status=status) 
        
    def inserir(self):
        return super().inserir()
    

# Classe para os turnos possíveis para solicitações
class Turno(db.Model):
    __tablename__ = 'turnos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Um turno pode estar associado a múltiplas solicitações
    solicitacoes = db.relationship('Solicitacao', back_populates='turno')
        
    def __repr__(self):
        return f"{self.name} ({self.hora_inicio} ~ {self.hora_fim})"
    
    def recuperar_tudo():
        return Turno.query.filter_by(ativo=True).all()
    
    def recuperar_id(turno_id):
        return Turno.query.filter_by(id=turno_id).filter_by(ativo=True).first_or_404()
    
    def criar(form):
        return Turno(name=form.nome.data, 
                     hora_inicio=form.hora_inicio.data, 
                     hora_fim=form.hora_fim.data)
    
    def inserir(self):
        db.session.add(self)
        db.session.commit()
    