from flask import abort, jsonify, render_template, request, flash, Blueprint
from flask_login import login_required, current_user

from app.models import Solicitacao

api = Blueprint('api', __name__)


@api.route("/solicitacoes")
def solicitacoes(): 
    solicitacoes = Solicitacao.recupera_todas()
    if solicitacoes:
        return {'data': [s.to_dict() for s in solicitacoes]}
        
@api.route("/solicitacoes/<int:solicitacao_id>", methods=['GET', 'DELETE'])
def solicitacao_id(solicitacao_id): 
    if request.method == 'GET':
        solicitacao = Solicitacao.recupera_id(solicitacao_id)
        return {'data': [solicitacao.to_dict()]}
    
    if request.method == 'DELETE':
        solicitacao = Solicitacao.recupera_id(solicitacao_id)
        Solicitacao.exclui(solicitacao)
        return {'message': 'Solicitação excluída com sucesso!'}
        