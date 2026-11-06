"""Teto de compra: um valor único do grupo, com o destaque derivado do Preço unitário (ticket 10; ADR-0003, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor, definir_conteudo, definir_teto, obter_teto
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, corrigir, informar_data_de_hoje
from importacao.casos_de_uso import confirmar_revisao, iniciar_importacao, informar_condicoes_do_catalogo, obter_revisao

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
        informar_data_de_hoje(self.gestora, revisao.pk)
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


    def revisao_com(self, cartoes):
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        return iniciar_importacao(self.gestora, self.alfa, arquivo, hoje=DIA)

    def destaques_da_revisao(self, revisao):
        return [(o.codigo, o.acima_do_teto) for o in obter_revisao(self.gestora, revisao.pk).ofertas_propostas()]

    def test_na_revisao_so_o_preco_unitario_acima_do_teto_e_destacado_e_acompanha_o_desconto(self):
        revisao = self.revisao_com([
            CartaoFicticio('1001', 'Item Ficticio A', '5,01'),
            CartaoFicticio('1002', 'Item Ficticio B', '5,00'),
        ])
        definir_teto(self.gestora, '5,00')
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)
        sem_desconto = self.destaques_da_revisao(revisao)

        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '10')  # 5,01 vira 4,51
        informar_data_de_hoje(self.gestora, revisao.pk)

        self.assertEqual(
            (sem_desconto, self.destaques_da_revisao(revisao)),
            ([('1001', True), ('1002', False)], [('1001', False), ('1002', False)]),
        )

    def test_na_revisao_o_destaque_usa_o_preco_unitario_com_conteudo(self):
        revisao = self.revisao_com([CartaoFicticio('1001', 'Kit 3 Item Ficticio', '9,00')])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)
        definir_teto(self.gestora, '5,00')
        sem_conteudo = self.destaques_da_revisao(revisao)

        kit = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()[0]
        corrigir(self.gestora, kit, conteudo='3')  # 3,00

        self.assertEqual((sem_conteudo, self.destaques_da_revisao(revisao)), ([('1001', True)], [('1001', False)]))

    def test_teto_vazio_zero_ou_negativo_e_recusado_e_o_teto_anterior_continua(self):
        definir_teto(self.gestora, '5,00')

        for digitado in ['', '   ', '0', '0,00', '-5,00', 'abc']:
            with self.subTest(digitado=digitado):
                with self.assertRaises(ErroDeNegocio) as erro:
                    definir_teto(self.gestora, digitado)
                self.assertEqual(erro.exception.mensagem, 'O Teto de compra precisa ser maior que zero.')
        self.assertEqual(obter_teto(self.gestora), Decimal('5.00'))

    def test_teto_grande_demais_e_recusado_e_o_teto_anterior_continua(self):
        definir_teto(self.gestora, '5,00')

        for digitado in ['10.000.000.000,00', '99999999999999,99']:
            with self.subTest(digitado=digitado):
                with self.assertRaises(ErroDeNegocio) as erro:
                    definir_teto(self.gestora, digitado)
                self.assertEqual(
                    erro.exception.mensagem, 'O Teto de compra é grande demais. Confira se digitou o valor certo.'
                )
        self.assertEqual(obter_teto(self.gestora), Decimal('5.00'))

    def test_teto_usa_a_mesma_leitura_de_preco_do_resto_do_sistema(self):
        # No Brasil o ponto separa milhar: "1.500" pode ser mil e quinhentos ou um real e cinquenta.
        definir_teto(self.gestora, '5,00')
        with self.assertRaises(ErroDeNegocio) as erro:
            definir_teto(self.gestora, '1.500')
        self.assertEqual(
            erro.exception.mensagem,
            'Use vírgula para os centavos: 1.500,00 para mil e quinhentos, 1,50 para um real e cinquenta.',
        )
        self.assertEqual(obter_teto(self.gestora), Decimal('5.00'))  # o recusado não apaga o anterior

        for digitado, valor in [('1.500,00', Decimal('1500.00')), ('12.5', Decimal('12.5')), ('7', Decimal('7'))]:
            with self.subTest(digitado=digitado):
                definir_teto(self.gestora, digitado)
                self.assertEqual(obter_teto(self.gestora), valor)
