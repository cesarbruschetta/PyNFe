# -*- coding: utf-8 -*-

from pynfe.entidades import ConsultaMigrate
from pynfe.utils import etree, so_numeros
from pynfe.utils.flags import VERSAO_PADRAO
from pynfe.processamento.serializacao import Serializacao


class SerializacaoConsultaMigrate(Serializacao):
    _versao = VERSAO_PADRAO

    def exportar(self, destino=None, retorna_string=False, limpar=True, **kwargs):
        """Gera o(s) arquivo(s) de Consulta Nota Fiscal eletronica
            no padrao oficial da migrate, invocity
        @param destino -
        @param retorna_string - Retorna uma string para debug.
        @param limpar - Limpa a fonte de dados para não gerar xml com dados duplicados.
        """
        try:
            # Carrega lista de Notas Fiscais
            consultas = self._fonte_dados.obter_lista(_classe=ConsultaMigrate,
                                                      **kwargs)

            for consulta in consultas:
                raiz = self._serializar_consulta(consulta, retorna_string=False)

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=False)
            else:
                return raiz
        except Exception as e:
            raise e

        finally:
            if limpar:
                self._fonte_dados.limpar_dados()

    def _serializar_consulta(self, consulta, tag_raiz='Consulta', retorna_string=True):

        raiz = etree.Element(tag_raiz)

        etree.SubElement(raiz, 'ModeloDocumento').text = 'NFCe'
        etree.SubElement(raiz, 'Versao').text = self._versao
        etree.SubElement(raiz, 'tpAmb').text = str(self._ambiente)
        etree.SubElement(raiz, 'CnpjEmissor').text = so_numeros(consulta.cnpj)
        etree.SubElement(raiz, 'Serie').text = str(consulta.serie)

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz


class SerializacaoConsultaPuloNumeracao(Serializacao):
    _versao = VERSAO_PADRAO

    def exportar(self, destino=None, retorna_string=False, limpar=True, **kwargs):
        """Gera o(s) arquivo(s) de Consulta Nota Fiscal eletronica
            no padrao oficial da migrate, invocity
        @param destino -
        @param retorna_string - Retorna uma string para debug.
        @param limpar - Limpa a fonte de dados para não gerar xml com dados duplicados.
        """
        try:
            # Carrega lista de Notas Fiscais
            consultas = self._fonte_dados.obter_lista(_classe=ConsultaMigrate,
                                                      **kwargs)

            for consulta in consultas:
                raiz = self._serializar_pulo(consulta, retorna_string=False)

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=False)
            else:
                return raiz
        except Exception as e:
            raise e

        finally:
            if limpar:
                self._fonte_dados.limpar_dados()

    def _serializar_pulo(self, consulta, tag_raiz='PuloNumeracao', retorna_string=True):

        raiz = etree.Element(tag_raiz)

        etree.SubElement(raiz, 'ModeloDocumento').text = 'NFCe'
        etree.SubElement(raiz, 'tpAmb').text = str(self._ambiente)
        etree.SubElement(raiz, 'CnpjEmpresa').text = so_numeros(consulta.cnpj)
        etree.SubElement(raiz, 'DocEmtCNPJ').text = so_numeros(consulta.cnpj)
        etree.SubElement(raiz, 'Serie').text = str(consulta.serie)
        etree.SubElement(
            raiz, 'DataEmissaoInicial').text = consulta.data_inicial.strftime("%Y-%m-%d")
        etree.SubElement(
            raiz, 'DataEmissaoFinal').text = consulta.data_final.strftime("%Y-%m-%d")

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz
