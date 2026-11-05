"""Marcas de conferência e contagem de preços na Revisão (ticket 08; ADR-0006).

As regras foram calibradas com os Catálogos reais; os números estão no ticket 08. Aqui, só dados inventados.
"""

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao, obter_revisao


def cartoes_com_precos(*precos):
    return [CartaoFicticio(str(1001 + i), f'Item Ficticio {i + 1}', preco) for i, preco in enumerate(precos)]


class MarcasDeConferenciaTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def importar(self, cartoes, rodape='Catálogo de Produtos Fornecedor Fictício'):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes, rodape=rodape))
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo)

    def marcas(self, revisao):
        return {oferta.codigo: oferta.marcas for oferta in obter_revisao(self.gestora, revisao.pk).ofertas_propostas()}

    def test_preco_mais_de_10_vezes_a_mediana_ou_menos_de_um_decimo_dela_fica_fora_do_padrao(self):
        # Mediana 10,00: 150,00 passa de 10 vezes; 0,90 fica abaixo de um décimo.
        revisao = self.importar(cartoes_com_precos('9,00', '10,00', '10,00', '11,00', '12,00', '150,00', '0,90'))

        self.assertEqual(
            self.marcas(revisao),
            {
                '1001': [], '1002': [], '1003': [], '1004': [], '1005': [],
                '1006': ['fora do padrão'],
                '1007': ['fora do padrão'],
            },
        )
