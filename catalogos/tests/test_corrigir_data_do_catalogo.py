"""Corrigir a data de um Catálogo confirmado (ticket 33; ADR-0009 item 6, ADR-0007; histórias 104 e 105)."""

from datetime import date

from catalogos.casos_de_uso import (
    buscar_ofertas,
    cadastrar_fornecedor,
    correcoes_da_data,
    corrigir_data_do_catalogo,
    obter_catalogo,
)
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, importar_e_confirmar

IMPORTADO_EM = date(2026, 10, 20)
HOJE = date(2026, 11, 6)


def cartoes(*codigos, preco='10,00'):
    return [CartaoFicticio(codigo, f'Item Ficticio {codigo}', preco, '6') for codigo in codigos]


def registro(correcao):
    return (correcao.gestor.get_username(), correcao.dia, correcao.data_anterior_exibida, correcao.data_nova_exibida)


class CorrigirDataDoCatalogoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')  # importa
        self.socio = criar_gestor('socio')  # corrige
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')
        self.beta = cadastrar_fornecedor(self.gestora, 'Beta')

    def importar(self, data, codigos, fornecedor=None, preco='10,00'):
        return importar_e_confirmar(
            self.gestora, fornecedor or self.alfa, cartoes(*codigos, preco=preco), data, IMPORTADO_EM
        )

    def corrigir(self, catalogo, texto, gestor=None):
        corrigir_data_do_catalogo(gestor or self.socio, catalogo.pk, texto, hoje=HOJE)
        return obter_catalogo(self.gestora, catalogo.pk)

    def test_qualquer_gestor_corrige_a_data_e_o_dia_da_importacao_nao_muda(self):
        catalogo = self.importar('15/10/2026', ['1001'])

        corrigido = self.corrigir(catalogo, '10/2025')

        self.assertEqual((corrigido.data_exibida, corrigido.importado_em), ('10/2025', IMPORTADO_EM))

    def test_formato_data_futura_e_ano_sao_recusados_com_as_mensagens_da_revisao_e_a_data_nao_muda(self):
        catalogo = self.importar('15/10/2026', ['1001'])
        casos = [
            ('outubro', 'Informe a data do Catálogo como dia/mês/ano ou mês/ano, por exemplo 15/10/2026 ou 10/2026.'),
            ('31/02/2026', 'Informe a data do Catálogo como dia/mês/ano ou mês/ano, por exemplo 15/10/2026 ou 10/2026.'),
            ('07/11/2026', 'A data do Catálogo não pode ser depois de hoje.'),
            ('12/2026', 'A data do Catálogo não pode ser depois de hoje.'),
            ('10/1999', 'Confira o ano da data do Catálogo.'),
        ]

        for texto, mensagem in casos:
            with self.subTest(texto=texto):
                with self.assertRaisesMessage(ErroDeNegocio, mensagem):
                    self.corrigir(catalogo, texto)
                self.assertEqual(obter_catalogo(self.gestora, catalogo.pk).data_exibida, '15/10/2026')

        self.assertEqual(self.corrigir(catalogo, '06/11/2026').data_exibida, '06/11/2026')  # hoje vale

    def test_a_correcao_registra_o_gestor_o_dia_e_as_datas_anterior_e_nova_como_foram_informadas(self):
        catalogo = self.importar('10/2026', ['1001'])

        self.corrigir(catalogo, '15/10/2026')

        self.assertEqual(
            [registro(c) for c in correcoes_da_data(self.gestora, catalogo.pk)],
            [('socio', HOJE, '10/2026', '15/10/2026')],
        )

    def test_as_correcoes_vem_da_mais_recente_para_a_mais_antiga(self):
        catalogo = self.importar('15/10/2026', ['1001'])
        corrigir_data_do_catalogo(self.socio, catalogo.pk, '10/2025', hoje=date(2026, 11, 2))
        corrigir_data_do_catalogo(self.gestora, catalogo.pk, '01/10/2025', hoje=date(2026, 11, 4))

        self.assertEqual(
            [registro(c) for c in correcoes_da_data(self.socio, catalogo.pk)],
            [
                ('gestora', date(2026, 11, 4), '10/2025', '01/10/2025'),
                ('socio', date(2026, 11, 2), '15/10/2026', '10/2025'),
            ],
        )

    def test_a_mesma_data_ja_guardada_nao_e_correcao_e_nada_e_registrado(self):
        catalogo = self.importar('15/10/2026', ['1001'])
        mes_e_ano = self.importar('10/2026', ['1002'])

        self.corrigir(catalogo, '15/10/2026')
        self.corrigir(catalogo, '15/10/26')  # a mesma data, digitada de outro jeito
        self.corrigir(mes_e_ano, '10/2026')

        self.assertEqual(list(correcoes_da_data(self.gestora, catalogo.pk)), [])
        self.assertEqual(list(correcoes_da_data(self.gestora, mes_e_ano.pk)), [])

    def test_mudar_so_a_precisao_da_data_e_correcao_decisao_da_usuaria(self):
        catalogo = self.importar('01/10/2026', ['1001'])

        self.assertEqual(self.corrigir(catalogo, '10/2026').data_exibida, '10/2026')

        self.assertEqual(
            [registro(c) for c in correcoes_da_data(self.gestora, catalogo.pk)],
            [('socio', HOJE, '01/10/2026', '10/2026')],
        )

    def test_corrigir_um_catalogo_que_nao_existe_e_recusado(self):
        with self.assertRaisesMessage(ErroDeNegocio, 'Catálogo não encontrado.'):
            corrigir_data_do_catalogo(self.socio, 999, '10/2025', hoje=HOJE)

    def test_depois_de_corrigir_a_busca_padrao_mostra_a_oferta_do_outro_catalogo(self):
        errado = self.importar('15/10/2026', ['1001'], preco='10,00')
        self.importar('01/09/2026', ['1001'], preco='12,00')
        self.assertEqual(self.vigentes('1001'), [('1001', '15/10/2026', '10.00')])

        self.corrigir(errado, '10/2025')

        self.assertEqual(self.vigentes('1001'), [('1001', '01/09/2026', '12.00')])

    def vigentes(self, texto):
        return [
            (o.codigo, o.catalogo.data_exibida, str(o.preco_unitario))
            for o in buscar_ofertas(self.gestora, texto, fornecedor=self.alfa).ofertas
        ]
