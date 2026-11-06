"""Aviso de Catálogo mais antigo na Revisão (ticket 33; ADR-0009 item 5, história 103)."""

from datetime import date

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, importar_e_confirmar
from importacao.casos_de_uso import informar_data_do_catalogo, iniciar_importacao, obter_revisao

HOJE = date(2026, 11, 5)
BALDE = CartaoFicticio('1001', 'Balde Ficticio', '9,90', '6')


class AvisoDeCatalogoMaisAntigoNaRevisaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')
        self.beta = cadastrar_fornecedor(self.gestora, 'Beta')

    def aviso_com_a_data(self, texto, fornecedor=None):
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a([BALDE]))
        revisao = iniciar_importacao(self.gestora, fornecedor or self.alfa, arquivo, hoje=HOJE)
        informar_data_do_catalogo(self.gestora, revisao.pk, texto, hoje=HOJE)
        return obter_revisao(self.gestora, revisao.pk).aviso_de_catalogo_mais_antigo

    def test_data_anterior_a_do_catalogo_mais_recente_do_fornecedor_mostra_o_aviso(self):
        importar_e_confirmar(self.gestora, self.alfa, [BALDE], '15/10/2026', HOJE)

        self.assertEqual(
            self.aviso_com_a_data('01/09/2026'),
            'Este Catálogo é mais antigo que o de 15/10/2026 deste Fornecedor: '
            'os códigos que estão nos dois continuam com o preço do mais recente.',
        )

    def test_catalogo_de_outro_fornecedor_nao_conta(self):
        importar_e_confirmar(self.gestora, self.beta, [BALDE], '15/10/2026', HOJE)

        self.assertEqual(self.aviso_com_a_data('01/09/2026'), '')

    def test_com_a_mesma_data_ou_mais_recente_nao_ha_aviso(self):
        importar_e_confirmar(self.gestora, self.alfa, [BALDE], '15/10/2026', HOJE)

        for texto in ['15/10/2026', '16/10/2026', '11/2026']:
            with self.subTest(texto=texto):
                self.assertEqual(self.aviso_com_a_data(texto), '')

    def test_fornecedor_sem_catalogos_nao_tem_aviso(self):
        self.assertEqual(self.aviso_com_a_data('01/01/2000'), '')

    def test_o_aviso_cita_o_catalogo_mais_recente_com_a_data_como_foi_informada(self):
        for data in ['01/09/2026', '10/2026', '15/09/2026']:
            importar_e_confirmar(self.gestora, self.alfa, [BALDE], data, HOJE)

        self.assertEqual(
            self.aviso_com_a_data('15/08/2026'),
            'Este Catálogo é mais antigo que o de 10/2026 deste Fornecedor: '
            'os códigos que estão nos dois continuam com o preço do mais recente.',
        )

    def test_so_mes_e_ano_conta_como_o_dia_1_do_mes(self):
        importar_e_confirmar(self.gestora, self.alfa, [BALDE], '01/10/2026', HOJE)
        self.assertEqual(self.aviso_com_a_data('10/2026'), '')

        importar_e_confirmar(self.gestora, self.alfa, [BALDE], '02/10/2026', HOJE)
        self.assertIn('mais antigo que o de 02/10/2026', self.aviso_com_a_data('10/2026'))
