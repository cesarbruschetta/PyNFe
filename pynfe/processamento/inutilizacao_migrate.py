# -*- coding: utf-8 -*-

import time

from pynfe.entidades import EventoInutilizacaoNotaMigrate
from pynfe.utils import etree, so_numeros
from pynfe.utils.flags import VERSAO_PADRAO
from pynfe.processamento.serializacao import Serializacao


class SerializacaoInutilizacaoMigrate(Serializacao):
    _versao = VERSAO_PADRAO

    def exportar(self, destino=None, retorna_string=False, limpar=True, **kwargs):
        """Gera o(s) arquivo(s) de Inutilizacao Nota Fiscal eletronica
            no padrao oficial da migrate, invocity
        @param destino -
        @param retorna_string - Retorna uma string para debug.
        @param limpar - Limpa a fonte de dados para não gerar xml com dados duplicados.
        """
        try:
            # Carrega lista de Notas Fiscais
            eventos = self._fonte_dados.obter_lista(_classe=EventoInutilizacaoNotaMigrate,
                                                    **kwargs)

            for evento in eventos:
                raiz = self._serializar_evento(evento, retorna_string=False)

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=False)
            else:
                return raiz
        except Exception as e:
            raise e

        finally:
            if limpar:
                self._fonte_dados.limpar_dados()

    def _serializar_evento(self, evento, tag_raiz='Inutilizacao', retorna_string=True):

        raiz = etree.Element(tag_raiz)

        etree.SubElement(raiz, 'ModeloDocumento').text = 'NFCe'
        etree.SubElement(raiz, 'Versao').text = self._versao
        etree.SubElement(raiz, 'tpAmb').text = str(self._ambiente)

        etree.SubElement(raiz, 'CnpjEmissor').text = so_numeros(evento.cnpj)
        etree.SubElement(raiz, 'NumeroInicial').text = str(evento.numero_inicial)
        etree.SubElement(raiz, 'NumeroFinal').text = str(evento.numero_final)
        etree.SubElement(raiz, 'Serie').text = str(evento.serie)
        etree.SubElement(raiz, 'Justificativa').text = evento.justificativa

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz
