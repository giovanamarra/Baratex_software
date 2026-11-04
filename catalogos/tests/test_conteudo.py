"""Conteúdo guardado por Fornecedor + código (ticket 07; ADR-0005, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor, historico_do_conteudo, obter_catalogo
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, corrigir
from importacao.casos_de_uso import (
    confirmar_revisao,
    iniciar_importacao,
    informar_condicoes_do_catalogo,
    obter_revisao,
)

SEGUNDA = date(2026, 3, 2)
TERCA = date(2026, 3, 3)


def alteracao(registro):
    return (registro.gestor.get_username(), registro.data, registro.valor_anterior, registro.valor_novo)


class ConteudoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def importar(self, cartoes, fornecedor=None, hoje=SEGUNDA, gestor=None):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(gestor or self.gestora, fornecedor or self.alfa, catalogo, hoje=hoje)
        informar_condicoes_do_catalogo(gestor or self.gestora, revisao.pk, '0')
        return revisao

    def ofertas(self, revisao):
        return obter_revisao(revisao.gestor, revisao.pk).ofertas_propostas()

    def confirmar_tesouras_com_conteudo_3(self, fornecedor=None):
        """Primeiro Catálogo: a gestora define Conteúdo 3 para o kit 1001 e confirma."""
        revisao = self.importar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')], fornecedor, SEGUNDA)
        corrigir(self.gestora, self.ofertas(revisao)[0], conteudo='3')
        return confirmar_revisao(self.gestora, revisao.pk, hoje=SEGUNDA)

    def test_definir_o_conteudo_na_revisao_recalcula_o_preco_unitario(self):
        revisao = self.importar([
            CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00'),
            CartaoFicticio('1002', 'Rodo Ficticio', '9,90'),
        ])
        tesouras = self.ofertas(revisao)[0]

        corrigir(self.gestora, tesouras, conteudo='3')

        self.assertEqual(
            [(oferta.codigo, oferta.conteudo, oferta.preco_unitario) for oferta in self.ofertas(revisao)],
            [('1001', 3, Decimal('3.00')), ('1002', 1, Decimal('9.90'))],
        )

    def test_ao_confirmar_o_conteudo_fica_guardado_por_fornecedor_e_codigo_com_o_gestor_e_a_data(self):
        revisao = self.importar([
            CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00'),
            CartaoFicticio('1002', 'Rodo Ficticio', '9,90'),
        ], hoje=SEGUNDA)
        corrigir(self.gestora, self.ofertas(revisao)[0], conteudo='3')

        catalogo = confirmar_revisao(self.gestora, revisao.pk, hoje=TERCA)

        self.assertEqual(
            [(o.codigo, o.conteudo, o.preco_unitario) for o in obter_catalogo(self.gestora, catalogo.pk).ofertas()],
            [('1001', 3, Decimal('3.00')), ('1002', 1, Decimal('9.90'))],
        )
        # A data do registro é o dia da confirmação, não o da Importação.
        self.assertEqual(
            [alteracao(r) for r in historico_do_conteudo(self.gestora, self.alfa, '1001')],
            [('gestora', TERCA, 1, 3)],
        )

    def test_no_catalogo_seguinte_do_mesmo_fornecedor_a_oferta_ja_chega_na_revisao_com_o_conteudo_guardado(self):
        self.confirmar_tesouras_com_conteudo_3()

        seguinte = self.importar([
            CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,30'),
            CartaoFicticio('1003', 'Pa Ficticia', '5,00'),
        ], hoje=TERCA)

        self.assertEqual(
            [(oferta.codigo, oferta.conteudo, oferta.preco_unitario) for oferta in self.ofertas(seguinte)],
            [('1001', 3, Decimal('3.10')), ('1003', 1, Decimal('5.00'))],
        )

    def test_confirmar_sem_mudar_o_conteudo_herdado_nao_cria_registro_novo_no_historico(self):
        self.confirmar_tesouras_com_conteudo_3()
        seguinte = self.importar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,30')], hoje=TERCA)
        # Corrigir o preço reenvia o Conteúdo herdado (3) como está, igual ao formulário de Corrigir.
        corrigir(self.gestora, self.ofertas(seguinte)[0], preco_impresso='9,60')

        catalogo = confirmar_revisao(self.gestora, seguinte.pk, hoje=TERCA)

        self.assertEqual([oferta.preco_unitario for oferta in catalogo.ofertas()], [Decimal('3.20')])
        self.assertEqual(
            [alteracao(r) for r in historico_do_conteudo(self.gestora, self.alfa, '1001')],
            [('gestora', SEGUNDA, 1, 3)],
        )
