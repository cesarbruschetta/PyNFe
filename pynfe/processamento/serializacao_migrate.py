# -*- coding: utf-8 -*-

import time

from pynfe.entidades import NotaFiscal
from pynfe.utils import etree, so_numeros, \
    obter_pais_por_codigo, obter_codigo_por_municipio
from pynfe.utils.flags import CODIGOS_ESTADOS, VERSAO_PADRAO
from pynfe.processamento.serializacao import Serializacao


class SerializacaoMigrate(Serializacao):
    _versao = VERSAO_PADRAO

    def exportar(self, destino=None, retorna_string=False, limpar=True, **kwargs):
        """Gera o(s) arquivo(s) de Nota Fiscal eletronica no padrao oficial da SEFAZ
        e Receita Federal, para ser(em) enviado(s) para o webservice ou para ser(em)
        armazenado(s) em cache local.
        @param destino -
        @param retorna_string - Retorna uma string para debug.
        @param limpar - Limpa a fonte de dados para não gerar xml com dados duplicados.
        """
        try:
            # Carrega lista de Notas Fiscais
            notas_fiscais = self._fonte_dados.obter_lista(_classe=NotaFiscal, **kwargs)

            for nf in notas_fiscais:
                raiz = self._serializar_nota_fiscal(nf, retorna_string=False)

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=False)
            else:
                return raiz
        except Exception as e:
            raise e

        finally:
            if limpar:
                self._fonte_dados.limpar_dados()

    def importar(self, origem):
        """Cria as instancias do PyNFe a partir de arquivos XML no formato padrao da
        SEFAZ e Receita Federal."""

        raise Exception('Metodo nao implementado')

    def _serializar_emitente(self, emitente, tag_raiz='emit', retorna_string=True):
        raiz = etree.Element(tag_raiz)

        # Dados do emitente
        etree.SubElement(raiz, 'CNPJ_emit').text = so_numeros(emitente.cnpj)
        etree.SubElement(raiz, 'xNome').text = emitente.razao_social
        etree.SubElement(raiz, 'xFant').text = emitente.nome_fantasia
        etree.SubElement(raiz, 'Email').text = ''

        # Endereço
        endereco = etree.SubElement(raiz, 'enderEmit')
        etree.SubElement(endereco, 'xLgr').text = emitente.endereco_logradouro
        etree.SubElement(endereco, 'nro').text = emitente.endereco_numero
        if emitente.endereco_complemento:
            etree.SubElement(endereco, 'xCpl').text = emitente.endereco_complemento
        etree.SubElement(endereco, 'xBairro').text = emitente.endereco_bairro
        etree.SubElement(endereco, 'cMun').text = obter_codigo_por_municipio(
            emitente.endereco_municipio, emitente.endereco_uf)
        etree.SubElement(endereco, 'xMun').text = emitente.endereco_municipio
        etree.SubElement(endereco, 'UF').text = emitente.endereco_uf
        etree.SubElement(endereco, 'CEP').text = so_numeros(emitente.endereco_cep)
        etree.SubElement(endereco, 'cPais').text = emitente.endereco_pais
        etree.SubElement(endereco, 'xPais').text = obter_pais_por_codigo(
            emitente.endereco_pais)
        if emitente.endereco_telefone:
            etree.SubElement(endereco, 'fone').text = emitente.endereco_telefone
        etree.SubElement(raiz, 'IE').text = emitente.inscricao_estadual
        # Inscricao Municipal
        if emitente.inscricao_municipal:
            etree.SubElement(raiz, 'IM').text = emitente.inscricao_municipal
        etree.SubElement(raiz, 'CRT').text = emitente.codigo_de_regime_tributario

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_cliente(self, cliente, modelo, tag_raiz='dest', retorna_string=True):
        raiz = etree.Element(tag_raiz)

        # Dados do cliente (distinatario)
        etree.SubElement(raiz, '%s_dest' % (cliente.tipo_documento)).text = so_numeros(
            cliente.numero_documento)
        if not self._so_cpf:
            if cliente.razao_social:
                etree.SubElement(raiz, 'xNome_dest').text = cliente.razao_social

            if any([cliente.endereco_logradouro, cliente.endereco_numero,
                    cliente.endereco_bairro, cliente.endereco_municipio,
                    cliente.endereco_uf, cliente.endereco_cep]):

                endereco = etree.SubElement(raiz, 'enderDest')
                if cliente.endereco_logradouro:
                    etree.SubElement(endereco, 'xLgr_dest').text = cliente.endereco_logradouro

                if cliente.endereco_numero:
                    etree.SubElement(endereco, 'nro_dest').text = cliente.endereco_numero

                if cliente.endereco_complemento:
                    etree.SubElement(endereco, 'xCpl').text = cliente.endereco_complemento

                if cliente.endereco_bairro:
                    etree.SubElement(endereco, 'xBairro_dest').text = cliente.endereco_bairro

                if cliente.endereco_municipio and cliente.endereco_uf:
                    etree.SubElement(endereco, 'xMun_dest').text = cliente.endereco_municipio
                    etree.SubElement(endereco, 'UF_dest').text = cliente.endereco_uf
                    etree.SubElement(endereco, 'cMun_dest').text = obter_codigo_por_municipio(
                        cliente.endereco_municipio, cliente.endereco_uf)

                if cliente.endereco_cep:
                    etree.SubElement(endereco, 'CEP_dest').text = so_numeros(
                        cliente.endereco_cep)

                etree.SubElement(endereco, 'cPais_dest').text = cliente.endereco_pais
                etree.SubElement(endereco, 'xPais_dest').text = obter_pais_por_codigo(
                    cliente.endereco_pais)

                if cliente.endereco_telefone:
                    etree.SubElement(endereco, 'fone_dest').text = so_numeros(
                        cliente.endereco_telefone)

        # Indicador da IE do destinatário: 1 – Contribuinte ICMSpagamento à vista;
        # 2 – Contribuinte isento de inscrição; 9 – Não Contribuinte
        if cliente.indicador_ie == 9:
            # 9 – Não Contribuinte
            etree.SubElement(raiz, 'indIEDest').text = '9'
        elif (cliente.indicador_ie == 2 or cliente.isento_icms) or cliente.inscricao_estadual.upper() == 'ISENTO':
            etree.SubElement(raiz, 'indIEDest').text = '2'
        else:
            # Indicador da IE do destinatário: 1 – Contribuinte ICMSpagamento à vista;
            etree.SubElement(raiz, 'indIEDest').text = str(cliente.indicador_ie)

        # E-mail
        if cliente.email:
            etree.SubElement(raiz, 'Email_dest').text = cliente.email

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_produto_servico(self, produto_servico, modelo, tag_raiz='detItem', retorna_string=True):
        raiz = etree.Element(tag_raiz)

        # Produto
        prod = etree.SubElement(raiz, 'prod')
        etree.SubElement(prod, 'cProd').text = str(produto_servico.codigo)
        etree.SubElement(prod, 'xProd').text = produto_servico.descricao
        etree.SubElement(prod, 'NCM').text = produto_servico.ncm
        # Codificação opcional que detalha alguns NCM. Formato: duas letras maiúsculas e 4 algarismos. Se a mercadoria se enquadrar em mais de uma codificação, informar até 8 codificações principais.
        #etree.SubElement(prod, 'NVE').text = ''
        etree.SubElement(prod, 'CFOP').text = produto_servico.cfop
        etree.SubElement(prod, 'uCOM').text = produto_servico.unidade_comercial
        etree.SubElement(prod, 'qCOM').text = str(
            produto_servico.quantidade_comercial or 0)
        etree.SubElement(prod, 'vUnCom').text = str('{:.2f}').format(
            produto_servico.valor_unitario_comercial or 0)
        etree.SubElement(prod, 'vProd').text = str(
            '{:.2f}').format(produto_servico.valor_total_bruto or 0)
        etree.SubElement(prod, 'cEANTrib').text = produto_servico.ean_tributavel
        etree.SubElement(prod, 'uTrib').text = produto_servico.unidade_tributavel
        etree.SubElement(prod, 'qTrib').text = str(produto_servico.quantidade_tributavel)
        etree.SubElement(prod, 'vUnTrib').text = str('{:.2f}').format(
            produto_servico.valor_unitario_tributavel)
        """ Indica se valor do Item (vProd) entra no valor total da NF-e (vProd)
            0=Valor do item (vProd) não compõe o valor total da NF-e
            1=Valor do item (vProd) compõe o valor total da NF-e (vProd) (v2.0)
        """
        etree.SubElement(prod, 'indTot').text = str(produto_servico.ind_total)

        # etree.SubElement(prod, 'EXTIPI').text = ''
        etree.SubElement(prod, 'vSeg').text = '0.00'
        etree.SubElement(prod, 'vDesc').text = str(produto_servico.valor_desconto)
        etree.SubElement(prod, 'vOutro_item').text = '0.00'
        etree.SubElement(prod, 'nTipoItem').text = '0'
        etree.SubElement(prod, 'dProd').text = '0'
        etree.SubElement(prod, 'xPed_item').text = '0'
        etree.SubElement(prod, 'nItemPed').text = '0'

        # Imposto
        imposto = etree.SubElement(raiz, 'imposto')

        # Lei da transparencia
        # Tributos aprox por item
        if produto_servico.valor_tributos_aprox:
            etree.SubElement(imposto, 'vTotTrib').text = str(
                '{:.2f}').format(produto_servico.valor_tributos_aprox)

        # ICMS
        icms_item = etree.SubElement(imposto, 'ICMS')
        etree.SubElement(icms_item, 'orig').text = str(produto_servico.icms_origem)
        etree.SubElement(icms_item, 'CST').text = str(produto_servico.icms_modalidade)
        etree.SubElement(icms_item, 'modBC').text = str(
            produto_servico.icms_modalidade_determinacao_bc)
        etree.SubElement(icms_item, 'vBC').text = str(
            produto_servico.icms_valor_base_calculo)
        etree.SubElement(icms_item, 'pICMS').text = str(produto_servico.icms_aliquota)
        etree.SubElement(icms_item, 'vICMS_icms').text = str(produto_servico.icms_valor)

        # PIS
        pis = etree.SubElement(imposto, 'PIS')
        etree.SubElement(pis, 'CST_pis').text = produto_servico.pis_modalidade

        # COFINS
        cofins_item = etree.SubElement(imposto, 'COFINS')
        etree.SubElement(
            cofins_item, 'CST_cofins').text = produto_servico.cofins_modalidade

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_nota_fiscal(self, nota_fiscal, tag_raiz='Envio', retorna_string=True):
        raiz = etree.Element(tag_raiz)

        etree.SubElement(raiz, 'ModeloDocumento').text = 'NFCe'
        etree.SubElement(raiz, 'Versao').text = self._versao

        # timezone Brasília -03:00
        tz = time.strftime("%z")

        # Dados da Nota Fiscal
        ide = etree.SubElement(raiz, 'ide')
        etree.SubElement(ide, 'cUF').text = CODIGOS_ESTADOS[nota_fiscal.uf]
        etree.SubElement(ide, 'natOp').text = nota_fiscal.natureza_operacao
        etree.SubElement(ide, 'indPag').text = str(nota_fiscal.forma_pagamento)
        etree.SubElement(ide, 'mod').text = str(nota_fiscal.modelo)
        etree.SubElement(ide, 'serie').text = nota_fiscal.serie
        etree.SubElement(ide, 'nNF').text = str(nota_fiscal.numero_nf)
        etree.SubElement(ide, 'dhEmi').text = nota_fiscal.data_emissao.strftime(
            '%Y-%m-%dT%H:%M:%S')
        etree.SubElement(ide, 'fusoHorario').text = "{}:{}".format(tz[:-2], tz[-2:])
        etree.SubElement(ide, 'tpNf').text = str(
            nota_fiscal.tipo_documento)  # 0=entrada 1=saida
        """ nfce suporta apenas operação interna
            Identificador de local de destino da operação 1=Operação interna;2=Operação interestadual;3=Operação com exterior.
        """
        if nota_fiscal.modelo == 65:
            etree.SubElement(ide, 'idDest').text = str(1)
        else:
            etree.SubElement(ide, 'idDest').text = str(nota_fiscal.indicador_destino)

        etree.SubElement(ide, 'cMunFg').text = nota_fiscal.municipio
        etree.SubElement(ide, 'tpImp').text = str(nota_fiscal.tipo_impressao_danfe)
        """ ### CONTINGENCIA ###
            1=Emissão normal (não em contingência);
            2=Contingência FS-IA, com impressão do DANFE em formulário de segurança;
            3=Contingência SCAN (Sistema de Contingência do Ambiente Nacional);
            4=Contingência DPEC (Declaração Prévia da Emissão em Contingência);
            5=Contingência FS-DA, com impressão do DANFE em formulário de segurança;
            6=Contingência SVC-AN (SEFAZ Virtual de Contingência do AN);
            7=Contingência SVC-RS (SEFAZ Virtual de Contingência do RS);
            9=Contingência off-line da NFC-e (as demais opções de contingência são válidas também para a NFC-e).
            Para a NFC-e somente estão disponíveis e são válidas as opções de contingência 5 e 9.
        """
        if self._contingencia != None:
            if nota_fiscal.forma_emissao == '1':
                nota_fiscal.forma_emissao = '9'
        etree.SubElement(ide, 'tpEmis').text = str(nota_fiscal.forma_emissao)
        etree.SubElement(ide, 'tpAmb').text = str(self._ambiente)
        etree.SubElement(ide, 'finNFe').text = str(nota_fiscal.finalidade_emissao)
        if nota_fiscal.modelo == 65:
            etree.SubElement(ide, 'indFinal').text = str(1)
            etree.SubElement(ide, 'indPres').text = str(1)
        else:
            etree.SubElement(ide, 'indFinal').text = str(nota_fiscal.cliente_final)
            etree.SubElement(ide, 'indPres').text = str(nota_fiscal.indicador_presencial)
        etree.SubElement(ide, 'procEmi').text = str(nota_fiscal.processo_emissao)

        # Emitente
        raiz.append(self._serializar_emitente(nota_fiscal.emitente, retorna_string=False))

        # Destinatário
        try:
            raiz.append(self._serializar_cliente(
                nota_fiscal.cliente, modelo=nota_fiscal.modelo, retorna_string=False))
        except AttributeError as e:
            # NFC-e pode ser gerada sem destinatário
            if nota_fiscal.modelo == 65:
                pass
            else:
                raise e

        # Itens
        det = etree.SubElement(raiz, 'det')
        for num, item in enumerate(nota_fiscal.produtos_e_servicos):
            detItem = self._serializar_produto_servico(
                item, modelo=nota_fiscal.modelo, retorna_string=False)

            det.append(detItem)

        # Totais
        total = etree.SubElement(raiz, 'total')
        icms_total = etree.SubElement(total, 'ICMStot')
        etree.SubElement(icms_total, 'vBC_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_base_calculo)
        etree.SubElement(icms_total, 'vICMS_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total)
        etree.SubElement(icms_total, 'vICMSDeson_ttlnfe').text = str('{:.2f}').format(
            nota_fiscal.totais_icms_desonerado)  # Valor Total do ICMS desonerado
        etree.SubElement(icms_total, 'vBCST_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_st_base_calculo)
        etree.SubElement(icms_total, 'vST_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_st_total)
        etree.SubElement(icms_total, 'vProd_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total_produtos_e_servicos)
        etree.SubElement(icms_total, 'vFrete_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total_frete)
        etree.SubElement(icms_total, 'vSeg_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total_seguro)
        etree.SubElement(icms_total, 'vDesc_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total_desconto)
        etree.SubElement(icms_total, 'vII_ttlnfe').text = '0.00'

        # Tributos
        etree.SubElement(icms_total, 'vIPI_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total_ipi)
        etree.SubElement(icms_total, 'vPIS_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_pis)
        etree.SubElement(icms_total, 'vCOFINS_ttlnfe').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_cofins)

        etree.SubElement(icms_total, 'vOutro').text = str('{:.2f}').format(
            nota_fiscal.totais_icms_outras_despesas_acessorias)
        etree.SubElement(icms_total, 'vNF').text = str(
            '{:.2f}').format(nota_fiscal.totais_icms_total_nota)
        if nota_fiscal.totais_tributos_aproximado:
            etree.SubElement(icms_total, 'vTotTrib_ttlnfe').text = str(
                '{:.2f}').format(nota_fiscal.totais_tributos_aproximado)

        # Somente NFC-e
        """ Grupo obrigatório para a NFC-e, a critério da UF. Não informar para a NF-e (modelo 55). """
        if nota_fiscal.modelo == 65:
            # Transporte
            transp = etree.SubElement(raiz, 'transp')
            etree.SubElement(transp, 'modFrete').text = str(9)

        # Informações adicionais
        if nota_fiscal.informacoes_adicionais_interesse_fisco or nota_fiscal.informacoes_complementares_interesse_contribuinte:
            info_ad = etree.SubElement(raiz, 'infAdic')
            if nota_fiscal.informacoes_adicionais_interesse_fisco:
                etree.SubElement(
                    info_ad, 'infAdFisco').text = nota_fiscal.informacoes_adicionais_interesse_fisco
            if nota_fiscal.informacoes_complementares_interesse_contribuinte:
                etree.SubElement(
                    info_ad, 'infCpl').text = nota_fiscal.informacoes_complementares_interesse_contribuinte

        # Guarda o xml da nota
        nota_fiscal.xml_danfe = etree.tostring(
            raiz, encoding="unicode", pretty_print=False)

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz
