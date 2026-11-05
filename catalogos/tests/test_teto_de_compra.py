"""Teto de compra: um valor único do grupo, com o destaque derivado do Preço unitário (ticket 10; ADR-0003, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor, definir_conteudo, definir_teto, obter_teto
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import confirmar_revisao, iniciar_importacao, informar_condicoes_do_catalogo

DIA = date(2026, 3, 2)


class TetoDeCompraTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')

    def importar(self, cartoes, desconto='0', dia=DIA):
        """Importa e confirma um Catálogo fictício do Layout A do Fornecedor Alfa."""
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(self.gestora, self.alfa, arquivo, hoje=dia)
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, desconto)
        return confirmar_revisao(self.gestora, revisao.pk, hoje=dia)

    def destaques_da_busca(self):
        """(código, acima do Teto) de cada Oferta da busca, na ordem dos códigos."""
        return [(o.codigo, o.acima_do_teto) for o in buscar_ofertas(self.gestora, 'ficticio').ofertas]

    def test_definir_o_teto_guarda_um_unico_valor_e_definir_de_novo_substitui(self):
        self.assertIsNone(obter_teto(self.gestora))

        definir_teto(self.gestora, '5,00')
        primeiro = obter_teto(self.gestora)
        definir_teto(self.gestora, '6,50')

        self.assertEqual((primeiro, obter_teto(self.gestora)), (Decimal('5.00'), Decimal('6.50')))

    def test_o_teto_e_do_grupo_e_outro_gestor_ve_o_mesmo_valor(self):
        outro = criar_gestor('gestor-b')

        definir_teto(self.gestora, '5,00')

        self.assertEqual(obter_teto(outro), Decimal('5.00'))

    def test_so_o_preco_unitario_acima_do_teto_e_destacado(self):
        self.importar([
            CartaoFicticio('1001', 'Item Ficticio A', '5,01'),
            CartaoFicticio('1002', 'Item Ficticio B', '5,00'),
            CartaoFicticio('1003', 'Item Ficticio C', '4,99'),
        ])
        definir_teto(self.gestora, '5,00')

        self.assertEqual(
            self.destaques_da_busca(), [('1001', True), ('1002', False), ('1003', False)]
        )

    def test_sem_teto_definido_nenhuma_oferta_e_destacada(self):
        self.importar([CartaoFicticio('1001', 'Item Ficticio A', '500,00')])

        self.assertEqual(self.destaques_da_busca(), [('1001', False)])

    def test_o_destaque_usa_o_preco_unitario_com_desconto_e_nao_o_preco_impresso(self):
        self.importar([CartaoFicticio('1001', 'Item Ficticio A', '5,50')], desconto='10')  # 4,95
        definir_teto(self.gestora, '5,00')

        self.assertEqual(self.destaques_da_busca(), [('1001', False)])

    def test_o_destaque_usa_o_preco_unitario_com_conteudo_e_nao_o_preco_impresso(self):
        self.importar([CartaoFicticio('1001', 'Kit 3 Item Ficticio', '9,00')])
        definir_conteudo(self.gestora, self.alfa, '1001', '3', hoje=DIA)  # 3,00
        definir_teto(self.gestora, '5,00')

        self.assertEqual(self.destaques_da_busca(), [('1001', False)])

    def test_mudar_o_teto_muda_o_destaque_na_proxima_consulta(self):
        self.importar([CartaoFicticio('1001', 'Item Ficticio A', '5,50')])
        definir_teto(self.gestora, '5,00')
        com_teto_5 = self.destaques_da_busca()

        definir_teto(self.gestora, '6,00')
        com_teto_6 = self.destaques_da_busca()

        self.assertEqual((com_teto_5, com_teto_6), ([('1001', True)], [('1001', False)]))
