from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao, informar_condicoes_do_catalogo, obter_revisao


def precos_unitarios(ofertas):
    return [oferta.preco_unitario for oferta in ofertas]


class PrecoUnitarioNaRevisaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def iniciar(self, cartoes):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo)

    def test_oferta_proposta_comeca_com_conteudo_1_e_sem_desconto_o_preco_unitario_e_o_impresso(self):
        revisao = self.iniciar([
            CartaoFicticio('1001', 'Balde Ficticio', '12,90'),
            CartaoFicticio('1002', 'Rodo Ficticio', '***,**'),  # sem preço, sem Preço unitário
        ])

        ofertas = revisao.ofertas_propostas()

        self.assertEqual([oferta.conteudo for oferta in ofertas], [1, 1])
        self.assertEqual(precos_unitarios(ofertas), [Decimal('12.90'), None])

    def test_informar_o_desconto_recalcula_o_preco_unitario_de_todas_as_ofertas(self):
        casos = [
            ('10', ['10,00'], [Decimal('9.00')]),  # exemplo do ticket
            ('3', ['9,99', '0,50'], [Decimal('9.69'), Decimal('0.49')]),  # 9,6903 e 0,485: meio centavo para cima
            ('2,5', ['10,00'], [Decimal('9.75')]),  # a gestora digita com vírgula
        ]
        for desconto, precos_impressos, esperados in casos:
            with self.subTest(desconto=desconto):
                revisao = self.iniciar(
                    [CartaoFicticio(str(1001 + n), 'Balde Ficticio', preco) for n, preco in enumerate(precos_impressos)]
                )

                informar_condicoes_do_catalogo(self.gestora, revisao.pk, desconto)

                ofertas = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()
                self.assertEqual(precos_unitarios(ofertas), esperados)
