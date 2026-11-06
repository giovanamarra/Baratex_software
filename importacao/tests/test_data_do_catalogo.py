"""Data do Catálogo informada na Revisão (ticket 31; ADR-0009, histórias 15, 101, 102)."""

from datetime import date

from catalogos.casos_de_uso import cadastrar_fornecedor
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import (
    confirmar_revisao,
    informar_condicoes_do_catalogo,
    informar_data_do_catalogo,
    iniciar_importacao,
    obter_revisao,
)

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

    def test_confirmar_sem_a_data_do_catalogo_e_recusado(self):
        informar_condicoes_do_catalogo(self.gestora, self.revisao.pk, '0')

        with self.assertRaisesMessage(ErroDeNegocio, 'Informe de quando é este Catálogo antes de confirmar.'):
            confirmar_revisao(self.gestora, self.revisao.pk)

    def test_sem_data_e_sem_desconto_a_recusa_lista_os_dois_numa_mensagem_so(self):
        with self.assertRaises(ErroDeNegocio) as recusa:
            confirmar_revisao(self.gestora, self.revisao.pk)

        self.assertEqual(
            recusa.exception.mensagem,
            'Informe o desconto do Catálogo antes de confirmar. Se não houver desconto, informe 0. '
            'Informe de quando é este Catálogo antes de confirmar.',
        )

    def test_data_depois_de_hoje_e_recusada_e_hoje_vale(self):
        with self.assertRaisesMessage(ErroDeNegocio, 'A data do Catálogo não pode ser depois de hoje.'):
            self.informar('06/11/2026')

        self.assertEqual(self.informar('05/11/2026'), '05/11/2026')
