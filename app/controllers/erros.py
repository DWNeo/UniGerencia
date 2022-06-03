from flask import Blueprint, render_template

erros = Blueprint('erros', __name__)

# Em caso de erro, essas funções redirecionam o usuário para 
# páginas personalizadas ao invés das páginas padrão
@erros.app_errorhandler(403)
def error_403(error):
    return render_template('erros/403.html', title='Erro 403'), 403


@erros.app_errorhandler(404)
def error_404(error):
    return render_template('erros/404.html', title='Erro 404'), 404


@erros.app_errorhandler(405)
def error_405(error):
    return render_template('erros/405.html', title='Erro 405'), 405


@erros.app_errorhandler(500)
def error_500(error):
    return render_template('erros/500.html', title='Erro 500'), 500
