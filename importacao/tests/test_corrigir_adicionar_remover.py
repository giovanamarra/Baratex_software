from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_catalogos_do_fornecedor
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, resumo
from importacao.casos_de_uso import (
    abandonar_revisao,
    adicionar_oferta_proposta,
    confirmar_revisao,
    corrigir_oferta_proposta,
    iniciar_importacao,
    informar_condicoes_do_catalogo,
    listar_revisoes_em_andamento,
    obter_revisao,
    remover_oferta_proposta,
)


class CorrigirAdicionarRemoverTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def iniciar(self, cartoes):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo)

    def ofertas(self, revisao):
        return obter_revisao(self.gestora, revisao.pk).ofertas_propostas()

    def test_corrigir_uma_oferta_mostra_os_valores_novos_e_recalcula_o_preco_unitario(self):
        revisao = self.iniciar([
            CartaoFicticio('1001', 'Balde Ficticio', '***,**', caixa='***'),
            CartaoFicticio('1002', 'Rodo Ficticio', '9,90'),
        ])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '10')
        balde = self.ofertas(revisao)[0]

        corrigir_oferta_proposta(
            self.gestora, balde.pk, codigo='1001-A', descricao='Balde Ficticio 10L', preco_impresso='15,00', caixa='12'
        )

        ofertas = self.ofertas(revisao)
        self.assertEqual(
            [resumo(oferta) + (oferta.preco_unitario,) for oferta in ofertas],
            [
                ('1001-A', 'Balde Ficticio 10L', Decimal('15.00'), 12, 'grade de cartões', Decimal('13.50')),
                ('1002', 'Rodo Ficticio', Decimal('9.90'), 24, 'grade de cartões', Decimal('8.91')),
            ],
        )
        self.assertEqual(obter_revisao(self.gestora, revisao.pk).desconto, Decimal('10'))

    def test_adicionar_uma_oferta_a_mao_faz_ela_aparecer_com_o_caminho_manual(self):
        revisao = self.iniciar([CartaoFicticio('1001', 'Balde Ficticio', '7,50')])

        adicionar_oferta_proposta(
            self.gestora, revisao.pk, codigo='2001', descricao='Esponja Ficticia', preco_impresso='3,40', caixa='60'
        )

        self.assertEqual(
            [resumo(oferta) for oferta in self.ofertas(revisao)],
            [
                ('1001', 'Balde Ficticio', Decimal('7.50'), 24, 'grade de cartões'),
                ('2001', 'Esponja Ficticia', Decimal('3.40'), 60, 'manual'),
            ],
        )

    def test_remover_uma_oferta_tira_ela_da_revisao_e_do_catalogo(self):
        revisao = self.iniciar([
            CartaoFicticio('1001', 'Balde Ficticio', '7,50'),
            CartaoFicticio('1002', 'Lixo de Leitura', '1,00'),
        ])
        lixo = self.ofertas(revisao)[1]

        remover_oferta_proposta(self.gestora, lixo.pk)

        self.assertEqual([oferta.codigo for oferta in self.ofertas(revisao)], ['1001'])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        catalogo = confirmar_revisao(self.gestora, revisao.pk)
        self.assertEqual([oferta.codigo for oferta in catalogo.ofertas()], ['1001'])

    def test_oferta_sem_preco_ou_com_preco_zero_fica_marcada(self):
        revisao = self.iniciar([
            CartaoFicticio('1001', 'Balde Ficticio', '7,50'),
            CartaoFicticio('1002', 'Rodo Ficticio', '***,**'),  # mascarado, como no real
            CartaoFicticio('1003', 'Pa Ficticia', '0,00'),
        ])

        self.assertEqual(
            [(oferta.codigo, oferta.marcas) for oferta in self.ofertas(revisao)],
            [('1001', []), ('1002', ['sem preço']), ('1003', ['preço zero'])],
        )

    def test_confirmacao_e_recusada_com_oferta_sem_caixa_e_passa_depois_de_informar_a_caixa(self):
        revisao = self.iniciar([
            CartaoFicticio('1001', 'Balde Ficticio', caixa='***'),  # mascarada, como no real
            CartaoFicticio('1002', 'Rodo Ficticio'),
            CartaoFicticio('1007', 'Pa Ficticia', caixa='***'),
        ])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')

        with self.assertRaisesMessage(
            ErroDeNegocio, 'Informe a Caixa antes de confirmar. Ofertas sem Caixa: 1001, 1007.'
        ):
            confirmar_revisao(self.gestora, revisao.pk)
        self.assertEqual([r.pk for r in listar_revisoes_em_andamento(self.gestora)], [revisao.pk])

        for oferta in self.ofertas(revisao):
            if oferta.caixa is None:
                self.corrigir(oferta, caixa='12')
        catalogo = confirmar_revisao(self.gestora, revisao.pk)

        self.assertEqual([oferta.caixa for oferta in catalogo.ofertas()], [12, 24, 12])

    def test_confirmacao_e_recusada_com_oferta_sem_preco_maior_que_zero(self):
        revisao = self.iniciar([
            CartaoFicticio('1001', 'Balde Ficticio', '7,50'),
            CartaoFicticio('1003', 'Rodo Ficticio', '***,**'),  # mascarado, como no real
            CartaoFicticio('1004', 'Pa Ficticia', '0,00'),
        ])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')

        with self.assertRaisesMessage(
            ErroDeNegocio, 'Informe um preço maior que zero antes de confirmar. Ofertas sem preço: 1003, 1004.'
        ):
            confirmar_revisao(self.gestora, revisao.pk)

        self.assertEqual([r.pk for r in listar_revisoes_em_andamento(self.gestora)], [revisao.pk])

    def test_correcoes_chegam_ao_catalogo_com_a_confirmacao_e_abandonar_descarta(self):
        cartoes = [CartaoFicticio('1001', 'Balde Ficticio', '7,50')]
        confirmada = self.iniciar(cartoes)
        abandonada = self.iniciar(cartoes)
        for revisao in (confirmada, abandonada):
            self.corrigir(self.ofertas(revisao)[0], descricao='Balde Ficticio 10L', preco_impresso='8,00')
            informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')

        catalogo = confirmar_revisao(self.gestora, confirmada.pk)
        abandonar_revisao(self.gestora, abandonada.pk)

        self.assertEqual(
            [resumo(oferta) for oferta in catalogo.ofertas()],
            [('1001', 'Balde Ficticio 10L', Decimal('8.00'), 24, 'grade de cartões')],
        )
        self.assertEqual(len(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)), 1)
        self.assertEqual(list(listar_revisoes_em_andamento(self.gestora)), [])

    def test_corrigir_com_preco_negativo_zero_ou_que_nao_e_numero_e_recusado(self):
        revisao = self.iniciar([CartaoFicticio('1001', 'Balde Ficticio', '7,50')])
        balde = self.ofertas(revisao)[0]

        for preco in ['-1,00', '0', '0,00', 'sete']:
            with self.subTest(preco=preco):
                with self.assertRaisesMessage(ErroDeNegocio, 'O preço precisa ser maior que zero.'):
                    self.corrigir(balde, preco_impresso=preco)

        self.assertEqual(self.ofertas(revisao)[0].preco_impresso, Decimal('7.50'))

    def corrigir(self, oferta, **mudancas):
        """Corrige só os campos pedidos, repetindo os outros como estão."""
        valores = {
            'codigo': oferta.codigo,
            'descricao': oferta.descricao,
            'preco_impresso': '' if oferta.preco_impresso is None else str(oferta.preco_impresso),
            'caixa': '' if oferta.caixa is None else str(oferta.caixa),
        }
        corrigir_oferta_proposta(self.gestora, oferta.pk, **{**valores, **mudancas})
