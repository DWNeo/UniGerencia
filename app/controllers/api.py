from datetime import datetime

from flask import abort, jsonify, render_template, request, flash, Blueprint
from flask_login import login_required, current_user

from app import db, fuso_horario
from app.models import Post, Equipamento, Sala, Solicitacao, Usuario
from app.utils import envia_email_atraso
from app.forms.solicitacoes import EntregaSolicitacaoForm

api = Blueprint('api', __name__)


@api.route("/solicitacoes", methods=['GET'])
def solicitacoes(): 
    solicitacoes = Solicitacao.recupera_todas()
    
    if solicitacoes:
        return jsonify({
            'data': [s.serialized for s in solicitacoes]
        })
        
@api.route("/solicitacoes/<int:solicitacao_id>", methods=['GET', 'DELETE'])
def solicitacao_id(solicitacao_id): 
    if request.method == 'GET':
        solicitacao = Solicitacao.recupera_id(solicitacao_id)

        return jsonify({
            'data': [solicitacao.serialized]
        })
    
    if request.method == 'DELETE':
        try:
            solicitacao = Solicitacao.recupera_id(solicitacao_id)
            Solicitacao.exclui(solicitacao)
            return jsonify({
                'message': 'Solicitação excluída com sucesso!'
            })
        except:
            abort(500)
        