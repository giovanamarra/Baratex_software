from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, resumo
from importacao.casos_de_uso import (
    adicionar_oferta_proposta,
    confirmar_revisao,
    corrigir_oferta_proposta,
    iniciar_importacao,
    informar_condicoes_do_catalogo,
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
