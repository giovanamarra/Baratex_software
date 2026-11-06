"""Corrigir a data de um Catálogo confirmado (ticket 33; ADR-0009 item 6, ADR-0007; histórias 104 e 105)."""

from datetime import date

from catalogos.casos_de_uso import cadastrar_fornecedor, corrigir_data_do_catalogo, obter_catalogo
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, importar_e_confirmar

IMPORTADO_EM = date(2026, 10, 20)
HOJE = date(2026, 11, 6)


def cartoes(*codigos, preco='10,00'):
    return [CartaoFicticio(codigo, f'Item Ficticio {codigo}', preco, '6') for codigo in codigos]


class CorrigirDataDoCatalogoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')  # importa
        self.socio = criar_gestor('socio')  # corrige
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')
        self.beta = cadastrar_fornecedor(self.gestora, 'Beta')

    def importar(self, data, codigos, fornecedor=None):
        return importar_e_confirmar(self.gestora, fornecedor or self.alfa, cartoes(*codigos), data, IMPORTADO_EM)

    def corrigir(self, catalogo, texto, gestor=None):
        corrigir_data_do_catalogo(gestor or self.socio, catalogo.pk, texto, hoje=HOJE)
        return obter_catalogo(self.gestora, catalogo.pk)

    def test_qualquer_gestor_corrige_a_data_e_o_dia_da_importacao_nao_muda(self):
        catalogo = self.importar('15/10/2026', ['1001'])

        corrigido = self.corrigir(catalogo, '10/2025')

        self.assertEqual((corrigido.data_exibida, corrigido.importado_em), ('10/2025', IMPORTADO_EM))
