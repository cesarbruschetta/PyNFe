# -*- coding: utf-8 -*-
from .emitente import Emitente


class Empresa(Emitente):
    """Empresa a ser cadastrada na migrate."""

    # - Apelido Na migrate
    apelido = str()

    # Email empresa
    email = str()

    # Tipo de endereco
    tipo_endereco = str()

    # DADOS DO USUARIO ROOT
    # Nome
    user_root_nome = str()

    # Email
    user_root_email = str()

    # Senha
    user_root_senha = str()

