from enum import Enum

class TipoTramite(str, Enum):
    licencia_construccion = "licencia_construccion"
    licencia_funcionamiento = "licencia_funcionamiento"
    permiso_transporte = "permiso_transporte"
    queja_vecinal = "queja_vecinal"
    certificado_domicilio = "certificado_domicilio"
    partida_nacimiento = "partida_nacimiento"
    autorizacion_sanitaria = "autorizacion_sanitaria"
    duplicado_dni = "duplicado_dni"
    exoneracion_tributaria = "exoneracion_tributaria"
    otro = "otro"