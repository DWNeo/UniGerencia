from app import login_manager

# Personaliza as mensagens de login
login_manager.login_message_category = 'info'
login_manager.needs_refresh_message_category = 'info'
login_manager.login_message = ('É necessário realizar login para acessar '
                               'essa página.')
login_manager.needs_refresh_message = 'É necessário realizar login novamente.'

# Personaliza as mensagens de erros de validação de formulário
obrigatorio = 'Este campo é obrigatório.'
max_10 = 'Este campo só pode ter até 10 caracteres.'
max_20 = 'Este campo só pode ter até 20 caracteres.'
max_50 = 'Este campo só pode ter até 50 caracteres.'
max_100 = 'Este campo só pode ter até 100 caracteres.'
max_200 = 'Este campo só pode ter até 200 caracteres.'
num_invalido = 'O valor inserido está fora da faixa permitida.'
identificacao_existente = 'Esta identificação já está sendo utilizada.'
email_invalido = 'O email inserido é inválido.'
email_inexistente = 'Não existe uma conta utilizando esse email.'
email_existente = 'Esse email já está sendo utilizado.'
patrimonio_existente = 'Já existe um equipamento com esse patrimônio.'
eqp_nome_existente = 'Já existe um equipamento com esse nome.'
sala_existente = 'Já existe uma sala com esse número.'
senha_diferente = 'As senhas inseridas não são iguais.'
imagem_invalida = 'Formato de imagem inválido.'
data_invalida = 'A data inserida não pode ser antes da data atual.'
