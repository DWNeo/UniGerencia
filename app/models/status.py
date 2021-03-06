import enum

# Classe Enum que define os status possíveis para diversos objetos
class Status(enum.Enum):
    ABERTO = 'Aberto'
    SOLICITADO = 'Solicitado' 
    CONFIRMADO = 'Confirmado'
    EMUSO = 'Em Uso'
    FECHADO = 'Finalizado'
    CANCELADO = 'Cancelado'
    PENDENTE = 'Pendente'
    EMMANUTENCAO = 'Em Manutenção'
    DESABILITADO = 'Desabilitado'
    