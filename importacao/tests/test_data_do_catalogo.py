"""Data do Catálogo informada na Revisão (ticket 31; ADR-0009, histórias 15, 101, 102)."""

from datetime import date

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import informar_data_do_catalogo, iniciar_importacao, obter_revisao

HOJE = date(2026, 11, 5)


class DataDoCatalogoNaRevisaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio', '9,90', '6')]))
        self.revisao = iniciar_importacao(self.gestora, self.fornecedor, arquivo, hoje=date(2026, 11, 2))

    def informar(self, texto):
        informar_data_do_catalogo(self.gestora, self.revisao.pk, texto, hoje=HOJE)
        return obter_revisao(self.gestora, self.revisao.pk).data_do_catalogo_exibida

    def test_aceita_a_data_completa_e_a_mostra_como_foi_informada(self):
        self.assertEqual(self.informar('15/10/2026'), '15/10/2026')

    def test_aceita_so_mes_e_ano(self):
        self.assertEqual(self.informar('10/2026'), '10/2026')

    def test_ano_com_2_digitos_e_deste_seculo(self):
        self.assertEqual(self.informar('15/10/26'), '15/10/2026')

    def test_ignora_espacos_nas_pontas(self):
        self.assertEqual(self.informar('  15/10/2026 '), '15/10/2026')

    def test_a_data_fica_no_rascunho_da_revisao_e_informar_de_novo_vale_a_ultima(self):
        self.informar('10/2026')

        self.assertEqual(self.informar('15/10/2026'), '15/10/2026')  # obter_revisao relê o rascunho do banco
        self.assertEqual(self.informar('09/2026'), '09/2026')
