# -*- coding: utf-8 -*-

"""
    @author: Cesar Augusto
"""

from .base import Entidade


class ConsultaMigrate(Entidade):

    modelo_documento = str()

    cnpj = str()

    serie = str()


class ConsultaPuloNumeracao(Entidade):

    modelo_documento = str()

    cnpj = str()

    serie = str()

    data_inicial = None

    data_final = None
