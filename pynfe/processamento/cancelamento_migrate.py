# -*- coding: utf-8 -*-

import time

from pynfe.entidades import EventoCancelarNotaMigrate
from pynfe.utils import etree, so_numeros
from pynfe.utils.flags import VERSAO_PADRAO
from pynfe.processamento.serializacao import Serializacao


class SerializacaoCancelamentoMigrate(Serializacao):
    _versao = VERSAO_PADRAO

    def exportar(self, destino=None, retorna_string=False, limpar=True, **kwargs):
        """Gera o(s) arquivo(s) de Cancelamento Nota Fiscal eletronica
            no padrao oficial da migrate, invocity
        @param destino -
        @param retorna_string - Retorna uma string para debug.
        @param limpar - Limpa a fonte de dados para não gerar xml com dados duplicados.
        """
        try:
            # Carrega lista de Notas Fiscais
            eventos = self._fonte_dados.obter_lista(_classe=EventoCancelarNotaMigrate,
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

    def _serializar_evento(self, evento, tag_raiz='EnvioEvento', retorna_string=True):

        raiz = etree.Element(tag_raiz)

        etree.SubElement(raiz, 'ModeloDocumento').text = 'NFCe'
        etree.SubElement(raiz, 'Versao').text = self._versao

        # timezone Brasília -03:00
        tz = time.strftime("%z")

        event = etree.SubElement(raiz, 'Evento')
        etree.SubElement(event, 'NtfCnpjEmissor').text = so_numeros(evento.cnpj)
        etree.SubElement(event, 'NtfNumero').text = evento.numero
        etree.SubElement(event, 'NtfSerie').text = evento.serie
        etree.SubElement(event, 'tpAmb').text = str(self._ambiente)

        eve_info = etree.SubElement(event, 'EveInf')
        etree.SubElement(eve_info, 'EveDh').text = evento.data_emissao.strftime(
            '%Y-%m-%dT%H:%M:%S')
        etree.SubElement(eve_info, 'EveFusoHorario').text = "{}:{}".format(
            tz[:-2], tz[-2:])
        etree.SubElement(eve_info, 'EveTp').text = evento.tp_evento
        etree.SubElement(eve_info, 'EvenSeq').text = str(evento.n_seq_evento)

        eve_det = etree.SubElement(eve_info, 'Evedet')
        etree.SubElement(eve_det, 'EveDesc').text = evento.descricao
        etree.SubElement(eve_det, 'EvenProt').text = evento.protocolo
        etree.SubElement(eve_det, 'EvexJust').text = evento.justificativa

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz
