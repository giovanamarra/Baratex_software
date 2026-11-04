"""Conteúdo guardado por Fornecedor + código (ticket 07; ADR-0005, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor, definir_conteudo, historico_do_conteudo, obter_catalogo
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, corrigir
from importacao.casos_de_uso import (
    abandonar_revisao,
    confirmar_revisao,
    iniciar_importacao,
    informar_condicoes_do_catalogo,
    obter_revisao,
)

SEGUNDA = date(2026, 3, 2)
TERCA = date(2026, 3, 3)
QUARTA = date(2026, 3, 4)


def alteracao(registro):
    return (registro.gestor.get_username(), registro.data, registro.valor_anterior, registro.valor_novo)


class ConteudoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')

    def importar(self, cartoes, fornecedor=None, hoje=SEGUNDA, gestor=None):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(gestor or self.gestora, fornecedor or self.alfa, catalogo, hoje=hoje)
        informar_condicoes_do_catalogo(gestor or self.gestora, revisao.pk, '0')
        return revisao

    def ofertas(self, revisao):
        return obter_revisao(revisao.gestor, revisao.pk).ofertas_propostas()

    def confirmar(self, cartoes, fornecedor=None, hoje=SEGUNDA):
        revisao = self.importar(cartoes, fornecedor, hoje)
        return confirmar_revisao(self.gestora, revisao.pk, hoje=hoje)

    def precos_unitarios(self, catalogo):
        return [
            (oferta.codigo, oferta.conteudo, oferta.preco_unitario)
            for oferta in obter_catalogo(self.gestora, catalogo.pk).ofertas()
        ]

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

    def test_o_mesmo_codigo_de_outro_fornecedor_continua_com_conteudo_1(self):
        beta = cadastrar_fornecedor(self.gestora, 'Beta')
        self.confirmar_tesouras_com_conteudo_3()

        do_beta = self.importar([CartaoFicticio('1001', 'Tesoura Ficticia Avulsa', '9,00')], beta, TERCA)

        self.assertEqual(
            [(oferta.codigo, oferta.conteudo, oferta.preco_unitario) for oferta in self.ofertas(do_beta)],
            [('1001', 1, Decimal('9.00'))],
        )
        self.assertEqual(list(historico_do_conteudo(self.gestora, beta, '1001')), [])

    def test_se_a_revisao_for_abandonada_o_conteudo_definido_nela_nao_e_guardado(self):
        abandonada = self.importar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')], hoje=SEGUNDA)
        corrigir(self.gestora, self.ofertas(abandonada)[0], conteudo='3')

        abandonar_revisao(self.gestora, abandonada.pk)

        seguinte = self.importar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')], hoje=TERCA)
        self.assertEqual([oferta.conteudo for oferta in self.ofertas(seguinte)], [1])
        self.assertEqual(list(historico_do_conteudo(self.gestora, self.alfa, '1001')), [])

    def test_definir_o_conteudo_fora_da_revisao_muda_o_preco_unitario_em_todos_os_catalogos_do_fornecedor_e_codigo(self):
        # É a regra, não um efeito colateral: o Conteúdo é guardado por Fornecedor + código, e não por
        # Oferta, então vale também para as Ofertas de Catálogos anteriores (ADR-0005; spec, Modelo de dados).
        beta = cadastrar_fornecedor(self.gestora, 'Beta')
        de_segunda = self.confirmar([
            CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00'),
            CartaoFicticio('1002', 'Rodo Ficticio', '9,90'),
        ], hoje=SEGUNDA)
        de_terca = self.confirmar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,30')], hoje=TERCA)
        do_beta = self.confirmar([CartaoFicticio('1001', 'Tesoura Ficticia Avulsa', '9,00')], beta, TERCA)

        definir_conteudo(self.gestora, self.alfa, '1001', '3', hoje=TERCA)

        self.assertEqual(
            self.precos_unitarios(de_segunda), [('1001', 3, Decimal('3.00')), ('1002', 1, Decimal('9.90'))]
        )
        self.assertEqual(self.precos_unitarios(de_terca), [('1001', 3, Decimal('3.10'))])
        self.assertEqual(self.precos_unitarios(do_beta), [('1001', 1, Decimal('9.00'))])

    def test_o_historico_do_conteudo_lista_gestor_data_valor_anterior_e_valor_novo(self):
        # O Conteúdo é dado do grupo (ADR-0007): outro Gestor também pode mudá-lo, e fica registrado.
        outro_gestor = criar_gestor('outro-gestor')
        self.confirmar_tesouras_com_conteudo_3()  # segunda: 1 -> 3, na confirmação da Revisão
        self.confirmar([CartaoFicticio('1002', 'Kit 2 Rodos Ficticios', '9,90')], hoje=SEGUNDA)

        definir_conteudo(outro_gestor, self.alfa, '1001', '6', hoje=TERCA)
        definir_conteudo(self.gestora, self.alfa, '1002', '2', hoje=TERCA)  # outro código: fora da lista
        definir_conteudo(self.gestora, self.alfa, '1001', '2', hoje=QUARTA)

        self.assertEqual(
            [alteracao(r) for r in historico_do_conteudo(self.gestora, self.alfa, '1001')],
            [
                ('gestora', QUARTA, 6, 2),
                ('outro-gestor', TERCA, 3, 6),
                ('gestora', SEGUNDA, 1, 3),
            ],
        )

    def test_conteudo_zero_negativo_fracionario_ou_que_nao_e_numero_e_recusado_na_revisao_e_fora_dela(self):
        catalogo = self.confirmar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')])
        revisao = self.importar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')], hoje=TERCA)
        na_revisao = self.ofertas(revisao)[0]
        mensagem = 'O Conteúdo precisa ser um número inteiro maior ou igual a 1.'

        for conteudo in ['0', '-1', '3,0', '2.5', 'tres', '']:
            with self.subTest(conteudo=conteudo, onde='na Revisão'):
                with self.assertRaisesMessage(ErroDeNegocio, mensagem):
                    corrigir(self.gestora, na_revisao, conteudo=conteudo)
            with self.subTest(conteudo=conteudo, onde='fora da Revisão'):
                with self.assertRaisesMessage(ErroDeNegocio, mensagem):
                    definir_conteudo(self.gestora, self.alfa, '1001', conteudo, hoje=TERCA)

        self.assertEqual([oferta.conteudo for oferta in self.ofertas(revisao)], [1])
        self.assertEqual(self.precos_unitarios(catalogo), [('1001', 1, Decimal('9.00'))])
        corrigir(self.gestora, na_revisao, conteudo=' 3 ')  # "3" vale, mesmo com espaços em volta
        self.assertEqual([oferta.conteudo for oferta in self.ofertas(revisao)], [3])

    def test_definir_fora_da_revisao_o_conteudo_de_um_codigo_sem_oferta_e_recusado(self):
        beta = cadastrar_fornecedor(self.gestora, 'Beta')
        self.confirmar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')])
        self.confirmar([CartaoFicticio('9999', 'Balde Ficticio', '7,50')], beta)  # o código existe, mas no Beta
        self.importar([CartaoFicticio('9999', 'Balde Ficticio', '7,50')])  # Oferta proposta ainda não é Oferta

        with self.assertRaisesMessage(ErroDeNegocio, 'O Fornecedor Alfa não tem Oferta com o código 9999.'):
            definir_conteudo(self.gestora, self.alfa, '9999', '3', hoje=TERCA)

        self.assertEqual(list(historico_do_conteudo(self.gestora, self.alfa, '9999')), [])
