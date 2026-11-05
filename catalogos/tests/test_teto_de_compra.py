"""Teto de compra: um valor único do grupo, com o destaque derivado do Preço unitário (ticket 10; ADR-0003, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor, definir_teto, obter_teto
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
