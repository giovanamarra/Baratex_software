"""Código repetido no mesmo Catálogo (ticket 32; ADR-0009, item 3). Só dados inventados."""

import io

from django.test import SimpleTestCase

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import (
    CARTOES_POR_PAGINA,
    CartaoFicticio,
    cartoes_com_o_segundo_na_pagina_2,
    catalogo_ficticio_layout_a,
)
from extracao.extrair import extrair_catalogo
from importacao.auxiliares_de_teste import (
    TesteComArquivosEnviados,
    arquivo_enviado,
    corrigir,
    informar_data_de_hoje,
)
from importacao.casos_de_uso import (
    adicionar_oferta_proposta,
    confirmar_revisao,
    informar_condicoes_do_catalogo,
    iniciar_importacao,
    obter_revisao,
    remover_oferta_proposta,
)


class PaginaDeOrigemTests(SimpleTestCase):
    def test_cada_oferta_extraida_guarda_a_pagina_de_origem(self):
        cartoes = cartoes_com_o_segundo_na_pagina_2(
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
        revisao = self.importar(cartoes_com_o_segundo_na_pagina_2(
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

    def repetido_duas_vezes(self):
        return self.importar([
            CartaoFicticio('1001', 'Panela Ficticia Secao A', '12,90'),
            CartaoFicticio('1002', 'Tampa Ficticia'),
            CartaoFicticio('1001', 'Panela Ficticia Secao B', '11,50'),
        ])

    def test_remover_uma_das_duas_tira_o_grupo_e_a_marca_da_que_ficou(self):
        revisao = self.repetido_duas_vezes()
        segunda = self.propostas(revisao)[1]

        remover_oferta_proposta(self.gestora, segunda.pk)

        self.assertEqual(
            [(o.descricao, o.marcas, o.ofertas_com_o_mesmo_codigo) for o in self.propostas(revisao)],
            [('Panela Ficticia Secao A', [], 1), ('Tampa Ficticia', [], 1)],
        )

    def test_corrigir_o_codigo_de_uma_delas_desfaz_o_grupo(self):
        revisao = self.repetido_duas_vezes()
        segunda = self.propostas(revisao)[1]

        corrigir(self.gestora, segunda, codigo='1003')

        self.assertEqual(
            [(o.codigo, o.marcas, o.ofertas_com_o_mesmo_codigo) for o in self.propostas(revisao)],
            [('1001', [], 1), ('1002', [], 1), ('1003', [], 1)],
        )

    def test_a_oferta_adicionada_com_espacos_nas_pontas_do_codigo_entra_no_grupo(self):
        revisao = self.importar([CartaoFicticio('1001', 'Panela Ficticia'), CartaoFicticio('1002', 'Tampa Ficticia')])

        adicionar_oferta_proposta(self.gestora, revisao.pk, '  1001 ', 'Panela Ficticia Digitada', '9,90', '12')

        self.assertEqual(
            [(o.descricao, o.marcas) for o in self.propostas(revisao)],
            [
                ('Panela Ficticia', ['código repetido']),
                ('Panela Ficticia Digitada', ['código repetido']),
                ('Tampa Ficticia', []),
            ],
        )

    def test_codigos_diferentes_so_em_maiusculas_nao_sao_o_mesmo_codigo(self):
        revisao = self.importar([CartaoFicticio('AB-10', 'Panela Ficticia'), CartaoFicticio('ab-10', 'Tampa Ficticia')])

        self.assertEqual(
            [(o.codigo, o.marcas) for o in self.propostas(revisao)], [('AB-10', []), ('ab-10', [])]
        )

    def test_a_confirmacao_nao_e_bloqueada_e_todas_as_repetidas_entram_no_catalogo_na_ordem_do_arquivo(self):
        revisao = self.repetido_duas_vezes()
        adicionar_oferta_proposta(self.gestora, revisao.pk, '1001', 'Panela Ficticia Digitada', '9,90', '12')
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)

        catalogo = confirmar_revisao(self.gestora, revisao.pk)

        self.assertEqual([o.descricao for o in catalogo.ofertas()], [
            'Panela Ficticia Secao A', 'Tampa Ficticia', 'Panela Ficticia Secao B', 'Panela Ficticia Digitada',
        ])

    def test_a_oferta_proposta_guarda_a_pagina_de_origem(self):
        revisao = self.importar(cartoes_com_o_segundo_na_pagina_2(
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
