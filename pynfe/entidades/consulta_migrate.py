# -*- coding: utf-8 -*-

"""
    @author: Cesar Augusto
"""

from .base import Entidade


class ConsultaMigrate(Entidade):

    modelo_documento = str()

    cnpj = str()

    serie = str()

    numero_inicial = str()

    numero_final = str()

    chave_acesso = str()

    data_inicial = None

    data_final = None


class ConsultaPuloNumeracao(Entidade):

    modelo_documento = str()

    cnpj = str()

    serie = str()

    data_inicial = None

    data_final = None
