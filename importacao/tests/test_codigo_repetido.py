"""Código repetido no mesmo Catálogo (ticket 32; ADR-0009, item 3). Só dados inventados."""

import io

from django.test import SimpleTestCase

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CARTOES_POR_PAGINA, CartaoFicticio, catalogo_ficticio_layout_a
from extracao.extrair import extrair_catalogo
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao, obter_revisao


def cartoes_com_repetido_na_pagina_2(primeiro, repetido):
    """O código 1001 no primeiro cartão da página 1 e no primeiro da página 2; os outros, códigos únicos."""
    outros = [CartaoFicticio(str(2001 + i), f'Item Ficticio {i + 1}') for i in range(CARTOES_POR_PAGINA - 1)]
    return [primeiro, *outros, repetido, CartaoFicticio('3001', 'Item Ficticio Final')]


class PaginaDeOrigemTests(SimpleTestCase):
    def test_cada_oferta_extraida_guarda_a_pagina_de_origem(self):
        cartoes = cartoes_com_repetido_na_pagina_2(
            CartaoFicticio('1001', 'Panela Ficticia Secao A'), CartaoFicticio('1001', 'Panela Ficticia Secao B')
        )

        extracao = extrair_catalogo(io.BytesIO(catalogo_ficticio_layout_a(cartoes)))

        paginas = [(oferta.codigo, oferta.pagina) for oferta in extracao.ofertas]
        self.assertEqual(paginas[0], ('1001', 1))
        self.assertEqual(paginas[CARTOES_POR_PAGINA - 1], (str(2001 + CARTOES_POR_PAGINA - 2), 1))
        self.assertEqual(paginas[CARTOES_POR_PAGINA:], [('1001', 2), ('3001', 2)])


class CodigoRepetidoNaRevisaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def importar(self, cartoes):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo)

    def propostas(self, revisao):
        return obter_revisao(self.gestora, revisao.pk).ofertas_propostas()

    def test_as_ofertas_do_mesmo_codigo_ficam_juntas_na_ordem_do_arquivo(self):
        revisao = self.importar(cartoes_com_repetido_na_pagina_2(
            CartaoFicticio('1001', 'Panela Ficticia Secao A', '12,90'),
            CartaoFicticio('1001', 'Panela Ficticia Secao B', '11,50'),
        ))

        ofertas = self.propostas(revisao)

        self.assertEqual(
            [(o.codigo, o.descricao) for o in ofertas[:3]],
            [('1001', 'Panela Ficticia Secao A'), ('1001', 'Panela Ficticia Secao B'), ('2001', 'Item Ficticio 1')],
        )
        self.assertEqual([o.codigo for o in ofertas[-2:]], [str(2001 + CARTOES_POR_PAGINA - 2), '3001'])
        self.assertEqual(len(ofertas), CARTOES_POR_PAGINA + 2)

    def test_cada_oferta_do_grupo_tem_a_marca_codigo_repetido_e_o_numero_de_ofertas_do_grupo(self):
        revisao = self.importar([
            CartaoFicticio('1001', 'Panela Ficticia Secao A', '12,90'),
            CartaoFicticio('1002', 'Tampa Ficticia'),
            CartaoFicticio('1001', 'Panela Ficticia Secao B', '11,50'),
            CartaoFicticio('1001', 'Panela Ficticia Secao C', '13,00'),
        ])

        self.assertEqual(
            [(o.codigo, o.marcas, o.ofertas_com_o_mesmo_codigo) for o in self.propostas(revisao)],
            [
                ('1001', ['código repetido'], 3),
                ('1001', ['código repetido'], 3),
                ('1001', ['código repetido'], 3),
                ('1002', [], 1),
            ],
        )

    def test_a_oferta_proposta_guarda_a_pagina_de_origem(self):
        revisao = self.importar(cartoes_com_repetido_na_pagina_2(
            CartaoFicticio('1001', 'Panela Ficticia Secao A'), CartaoFicticio('1001', 'Panela Ficticia Secao B')
        ))

        grupo = self.propostas(revisao)[:2]

        self.assertEqual([(o.descricao, o.pagina) for o in grupo], [
            ('Panela Ficticia Secao A', 1), ('Panela Ficticia Secao B', 2),
        ])

    def test_a_oferta_sem_preco_do_grupo_tambem_tem_a_marca_codigo_repetido(self):
        revisao = self.importar([
            CartaoFicticio('1001', 'Panela Ficticia Secao A', '12,90'),
            CartaoFicticio('1001', 'Panela Ficticia Secao B', preco=None),
        ])

        self.assertEqual(
            [o.marcas for o in self.propostas(revisao)],
            [['código repetido'], ['sem preço', 'código repetido']],
        )
