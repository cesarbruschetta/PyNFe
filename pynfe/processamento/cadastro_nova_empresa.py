# -*- coding: utf-8 -*-

from pynfe.entidades import Empresa
from pynfe.utils import etree, so_numeros, obter_codigo_por_municipio
from pynfe.utils.flags import VERSAO_PADRAO
from pynfe.processamento.serializacao import Serializacao


class SerializacaoCadastroEmpresa(Serializacao):
    _versao = VERSAO_PADRAO

    def exportar(self, destino=None, retorna_string=False, limpar=True, **kwargs):
        """Gera o arquivo de cadastro da empresa na migrate.
        @param destino -
        @param retorna_string - Retorna uma string para debug.
        @param limpar - Limpa a fonte de dados para não gerar xml com dados duplicados.
        """
        try:
            # Carrega lista de Empresas
            empresas = self._fonte_dados.obter_lista(_classe=Empresa, **kwargs)

            for ep in empresas:
                raiz = self._serializar_empresa(ep, retorna_string=False)

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=False)
            else:
                return raiz
        except Exception as e:
            raise e

        finally:
            if limpar:
                self._fonte_dados.limpar_dados()

    def _serializar_usuario(self, usuario, tag_raiz='Usuarios', retorna_string=True):

        def _serializar_permissoes(tag_raiz='Permissoes', retorna_string=True):
            raiz = etree.Element(tag_raiz)

            # Permissões referente ao módulo NFC-e
            p_nfce = etree.SubElement(raiz, 'PermissaoNFCe')
            etree.SubElement(p_nfce, 'Visualizar').text = "S"
            etree.SubElement(p_nfce, 'Baixar').text = "S"

            # Permissões gerais da aplicação
            p_geral = etree.SubElement(raiz, 'PermissoesGerais')
            etree.SubElement(p_geral, 'ImportarDocumentos').text = "N"
            etree.SubElement(p_geral, 'AlterarDadosDoUsuario').text = "S"
            etree.SubElement(p_geral, 'AlterarDadosDaEmpresa').text = "N"
            etree.SubElement(p_geral, 'AlterarMarcasDaEmpresa').text = "N"
            etree.SubElement(p_geral, 'AlterarCertificadosDaEmpresa').text = "S"
            etree.SubElement(p_geral, 'AlterarConfiguracoesParametros').text = "N"
            etree.SubElement(p_geral, 'CadastrarEmpresas').text = "N"
            etree.SubElement(p_geral, 'AlterarCaixasDeEmail').text = "S"
            etree.SubElement(p_geral, 'AlterarPermissoesDeUsuario').text = "S"
            etree.SubElement(p_geral, 'AdicionarNovosUsuarios').text = "S"
            etree.SubElement(p_geral, 'VisualizarChaveAcesso').text = "N"
            etree.SubElement(p_geral, 'VisualizarAcoesDeUsuarios').text = "S"
            etree.SubElement(p_geral, 'VisualizarQuantidadesEmitidas').text = "S"
            etree.SubElement(p_geral, 'VisualizarLicencas').text = "S"
            etree.SubElement(p_geral, 'ConfiguracaoSenha').text = "N"
            etree.SubElement(p_geral, 'GerarRelatorios').text = "S"
            etree.SubElement(p_geral, 'InutilizarDocumentos').text = "S"
            etree.SubElement(p_geral, 'FerramentasIntegracao').text = "N"

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=True)
            else:
                return raiz

        raiz = etree.Element(tag_raiz)

        # Dados do usuario
        item = etree.SubElement(raiz, 'UsuariosItem')
        etree.SubElement(item, 'UsrNome').text = usuario.user_root_nome
        etree.SubElement(item, 'UsrEmail').text = usuario.user_root_email
        etree.SubElement(item, 'UsrSenha').text = usuario.user_root_senha
        # 1 - Gerente; 2 - Digitador; 3 - Nenhum
        etree.SubElement(item, 'GrupoUsuario').text = '3'

        # Permissoes
        item.append(_serializar_permissoes(retorna_string=False))

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_parametros(self, empresa, tag_raiz='Parametros', retorna_string=True):

        def _serializar_parametros_nfce(tag_raiz='NFCe', retorna_string=True):

            def _serializar_contingencia(tag_raiz='OrdemContingencia',
                                         retorna_string=True):
                raiz = etree.Element(tag_raiz)

                orderm = etree.SubElement(raiz, 'OrdemContingenciaItem')
                etree.SubElement(orderm, 'OrdemContingenciaNFCe').text = '0'

                if retorna_string:
                    return etree.tostring(raiz, encoding="unicode", pretty_print=True)
                else:
                    return raiz

            # Parâmetros referente ao módulo NFC-e
            raiz = etree.Element(tag_raiz)
            etree.SubElement(
                raiz, 'InutilizarAutomaticamenteDocumentosRejeitados').text = 'N'
            etree.SubElement(raiz, 'InutilizarPulosNumeracao').text = 'N'
            etree.SubElement(raiz, 'FormaRetornoPDFIntegracao').text = '3'
            etree.SubElement(raiz, 'FormaRetornoXMLIntegracao').text = '3'
            etree.SubElement(raiz, 'UltimoNSU').text = '000000000000000'
            etree.SubElement(raiz, 'IDTokenCscSEFAZ').text = empresa.token
            etree.SubElement(raiz, 'CscSEFAZ').text = empresa.csc
            etree.SubElement(raiz, 'PossuiLeituraX').text = 'S'
            etree.SubElement(raiz, 'PossuiGeracaoRelatorios').text = 'S'

            raiz.append(_serializar_contingencia(retorna_string=False))

            if retorna_string:
                return etree.tostring(raiz, encoding="unicode", pretty_print=True)
            else:
                return raiz

        raiz = etree.Element(tag_raiz)
        etree.SubElement(raiz, 'OrientDANFE').text = '1'
        etree.SubElement(raiz, 'InfCplVerso').text = 'N'
        etree.SubElement(raiz, 'DhImpressao').text = 'S'
        etree.SubElement(raiz, 'ImpTributos').text = '3'
        etree.SubElement(raiz, 'DescICMS').text = 'N'
        etree.SubElement(raiz, 'EnviarPDFEmail').text = 'N'
        etree.SubElement(raiz, 'EnviarXMLEmail').text = 'N'
        etree.SubElement(raiz, 'ReaprovDocsRejeitados').text = 'N'
        etree.SubElement(raiz, 'InutPulosNumeracao').text = 'N'
        etree.SubElement(raiz, 'IdTokenNFCe').text = empresa.token
        etree.SubElement(raiz, 'CSCNFCe').text = empresa.csc

        # NFC-e
        raiz.append(_serializar_parametros_nfce(retorna_string=False))

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_licenciamento(self, empresa, tag_raiz='Licenciamento',
                                  retorna_string=True):
        raiz = etree.Element(tag_raiz)

        item = etree.SubElement(raiz, 'LicenciamentoItem')
        etree.SubElement(item, 'Modulo').text = 'NFCe'
        etree.SubElement(item, 'Modelo').text = '2'

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_certificado(self, empresa, tag_raiz='Certificado',
                                retorna_string=True):
        raiz = etree.Element(tag_raiz)

        etree.SubElement(raiz, 'ArquivoPFX').text = empresa.certificado_pfx
        etree.SubElement(raiz, 'Senha').text = empresa.senha_certificado

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz

    def _serializar_empresa(self, empresa, tag_raiz='CadastroEmpresa',
                            retorna_string=True):
        raiz = etree.Element(tag_raiz)

        # Dados do empresa
        etree.SubElement(raiz, 'EmpCNPJ').text = so_numeros(empresa.cnpj)
        etree.SubElement(raiz, 'EmpRazSocial').text = empresa.razao_social
        etree.SubElement(raiz, 'EmpNomFantasia').text = empresa.nome_fantasia
        etree.SubElement(raiz, 'EmpApelido').text = empresa.apelido
        etree.SubElement(raiz, 'EmpIE').text = empresa.inscricao_estadual

        # Inscricao Municipal
        if empresa.inscricao_municipal:
            etree.SubElement(raiz, 'EmpIM').text = so_numeros(empresa.inscricao_municipal)

        # Endereço
        etree.SubElement(raiz, 'EmpEndereco').text = empresa.endereco_logradouro
        etree.SubElement(raiz, 'EmpNumero').text = empresa.endereco_numero
        if empresa.endereco_complemento:
            etree.SubElement(raiz, 'EmpComplemento').text = empresa.endereco_complemento
        etree.SubElement(raiz, 'EmpBairro').text = empresa.endereco_bairro
        etree.SubElement(raiz, 'MunCodigo').text = obter_codigo_por_municipio(
            empresa.endereco_municipio, empresa.endereco_uf)
        etree.SubElement(raiz, 'EmpCEP').text = so_numeros(empresa.endereco_cep)

        if empresa.endereco_telefone:
            etree.SubElement(raiz, 'EmpTelefone').text = empresa.endereco_telefone

        etree.SubElement(raiz, 'EmpCNAE').text = empresa.cnae_fiscal
        etree.SubElement(raiz, 'EmpCRT').text = empresa.codigo_de_regime_tributario
        etree.SubElement(raiz, 'EmpIEST').text = ''
        etree.SubElement(raiz, 'EmpMarca').text = ''
        etree.SubElement(raiz, 'EmpMarcaExtensao').text = ''
        etree.SubElement(raiz, 'EmpEmail').text = empresa.email
        etree.SubElement(raiz, 'EmpTpoEndereco').text = empresa.tipo_endereco

        # Certificado
        raiz.append(self._serializar_certificado(empresa, retorna_string=False))

        # Usuarios
        raiz.append(self._serializar_usuario(empresa, retorna_string=False))

        # Parametros
        raiz.append(self._serializar_parametros(empresa, retorna_string=False))

        # Licenciamento
        raiz.append(self._serializar_licenciamento(empresa, retorna_string=False))

        if retorna_string:
            return etree.tostring(raiz, encoding="unicode", pretty_print=True)
        else:
            return raiz
