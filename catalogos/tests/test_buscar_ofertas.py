"""Buscar Ofertas vigentes (ticket 09; ADR-0005, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import confirmar_revisao, iniciar_importacao, informar_condicoes_do_catalogo

DIA_01 = date(2026, 3, 1)
DIA_15 = date(2026, 3, 15)


def achado(oferta):
    return (
        oferta.codigo,
        oferta.descricao,
        oferta.preco_unitario,
        oferta.caixa,
        oferta.catalogo.fornecedor.nome,
        oferta.catalogo.data,
    )


class BuscarOfertasTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')
        self.beta = cadastrar_fornecedor(self.gestora, 'Beta')

    def importar(self, cartoes, dia, fornecedor=None, desconto='0', gestor=None):
        """Importa e confirma um Catálogo fictício do Layout A, no dia dado."""
        gestor = gestor or self.gestora
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(gestor, fornecedor or self.alfa, arquivo, hoje=dia)
        informar_condicoes_do_catalogo(gestor, revisao.pk, desconto)
        return confirmar_revisao(gestor, revisao.pk, hoje=dia)

    def buscar(self, texto='', **filtros):
        return buscar_ofertas(self.gestora, texto, **filtros).ofertas

    def test_acha_pelo_codigo_e_mostra_codigo_descricao_preco_unitario_caixa_fornecedor_e_data(self):
        self.importar([
            CartaoFicticio('1001', 'Balde Ficticio', '9,90', caixa='24'),
            CartaoFicticio('1002', 'Rodo Ficticio', '12,00'),
        ], DIA_01)

        achadas = self.buscar('1001')

        self.assertEqual(
            [achado(o) for o in achadas],
            [('1001', 'Balde Ficticio', Decimal('9.90'), 24, 'Alfa', DIA_01)],
        )
