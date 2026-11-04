from datetime import date
from decimal import Decimal

from django.db import IntegrityError

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_catalogos_do_fornecedor
from catalogos.models import Oferta
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import (
    TesteComArquivosEnviados,
    TesteTransacionalComArquivosEnviados,
    arquivo_enviado,
    resumo,
)
from importacao.casos_de_uso import (
    abandonar_revisao,
    confirmar_revisao,
    iniciar_importacao,
    listar_revisoes_em_andamento,
)


class ConfirmarOuAbandonarRevisaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def iniciar(self, cartoes=None, hoje=None):
        cartoes = cartoes or [CartaoFicticio('1001', 'Balde Ficticio')]
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        if hoje is None:
            return iniciar_importacao(self.gestora, self.fornecedor, catalogo)
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo, hoje=hoje)

    def test_antes_de_confirmar_o_fornecedor_continua_sem_catalogos(self):
        self.iniciar()

        self.assertEqual(list(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)), [])

    def test_confirmar_cria_o_catalogo_com_as_ofertas_da_revisao(self):
        conteudo = catalogo_ficticio_layout_a([
            CartaoFicticio('1001', 'Balde Ficticio', '7,50', '6'),
            CartaoFicticio('1002', 'Rodo Ficticio', '***,**', '12'),  # sem preço: o bloqueio é do ticket 06
            CartaoFicticio('1003', 'Pa Ficticia', '3,20', '***'),  # sem Caixa: idem
        ])
        revisao = iniciar_importacao(self.gestora, self.fornecedor, arquivo_enviado(conteudo))

        catalogo = confirmar_revisao(self.gestora, revisao.pk)

        self.assertEqual((catalogo.fornecedor.nome, catalogo.gestor.username), ('Fornecedor Alfa', 'gestora'))
        with catalogo.arquivo.open('rb') as arquivo_de_origem:
            self.assertEqual(arquivo_de_origem.read(), conteudo)
        self.assertEqual(
            [resumo(oferta) for oferta in catalogo.ofertas()],
            [
                ('1001', 'Balde Ficticio', Decimal('7.50'), 6, 'grade de cartões'),
                ('1002', 'Rodo Ficticio', None, 12, 'grade de cartões'),
                ('1003', 'Pa Ficticia', Decimal('3.20'), None, 'grade de cartões'),
            ],
        )

    def test_data_do_catalogo_e_o_dia_em_que_a_importacao_comecou(self):
        revisao = self.iniciar(hoje=date(2026, 10, 10))

        catalogo = confirmar_revisao(self.gestora, revisao.pk)  # confirmada hoje, não no dia 10

        self.assertEqual(catalogo.data, date(2026, 10, 10))

    def test_lista_de_catalogos_do_fornecedor_mostra_o_catalogo_confirmado_com_a_data(self):
        revisao = self.iniciar(hoje=date(2026, 10, 10))
        confirmar_revisao(self.gestora, revisao.pk)

        catalogos = listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)

        self.assertEqual(
            [(catalogo.data, catalogo.fornecedor.nome) for catalogo in catalogos],
            [(date(2026, 10, 10), 'Fornecedor Alfa')],
        )

    def test_duas_importacoes_em_dias_diferentes_geram_dois_catalogos_e_o_primeiro_fica_intacto(self):
        primeira = self.iniciar([CartaoFicticio('1001', 'Balde Ficticio', '7,50')], hoje=date(2026, 10, 10))
        confirmar_revisao(self.gestora, primeira.pk)
        segunda = self.iniciar(
            [CartaoFicticio('1001', 'Balde Ficticio', '8,20'), CartaoFicticio('1002', 'Rodo Ficticio', '11,00')],
            hoje=date(2026, 10, 11),
        )
        confirmar_revisao(self.gestora, segunda.pk)

        catalogos = list(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor))

        self.assertEqual([catalogo.data for catalogo in catalogos], [date(2026, 10, 11), date(2026, 10, 10)])
        self.assertEqual(
            [resumo(oferta) for oferta in catalogos[1].ofertas()],
            [('1001', 'Balde Ficticio', Decimal('7.50'), 24, 'grade de cartões')],
        )

    def test_revisao_confirmada_sai_das_revisoes_em_andamento(self):
        confirmada = self.iniciar()
        em_andamento = self.iniciar()

        confirmar_revisao(self.gestora, confirmada.pk)

        self.assertEqual([revisao.pk for revisao in listar_revisoes_em_andamento(self.gestora)], [em_andamento.pk])

    def test_abandonar_nao_cria_catalogo_tira_a_revisao_da_lista_e_apaga_o_arquivo(self):
        revisao = self.iniciar()
        armazenamento, nome_do_arquivo = revisao.arquivo.storage, revisao.arquivo.name
        self.assertTrue(armazenamento.exists(nome_do_arquivo))

        abandonar_revisao(self.gestora, revisao.pk)

        self.assertFalse(armazenamento.exists(nome_do_arquivo))
        self.assertEqual(list(listar_revisoes_em_andamento(self.gestora)), [])
        self.assertEqual(list(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)), [])

    def test_confirmar_uma_revisao_ja_confirmada_e_recusado(self):
        revisao = self.iniciar()
        confirmar_revisao(self.gestora, revisao.pk)

        with self.assertRaisesMessage(ErroDeNegocio, 'Esta Revisão já foi confirmada.'):
            confirmar_revisao(self.gestora, revisao.pk)

        self.assertEqual(len(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)), 1)

    def test_abandonar_uma_revisao_ja_confirmada_e_recusado_e_o_catalogo_fica_intacto(self):
        revisao = self.iniciar()
        catalogo = confirmar_revisao(self.gestora, revisao.pk)

        with self.assertRaisesMessage(ErroDeNegocio, 'Esta Revisão já foi confirmada.'):
            abandonar_revisao(self.gestora, revisao.pk)

        self.assertEqual(len(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)), 1)
        self.assertTrue(catalogo.arquivo.storage.exists(catalogo.arquivo.name))

    def test_confirmar_ou_abandonar_uma_revisao_que_nao_existe_mais_e_recusado(self):
        revisao = self.iniciar()
        abandonar_revisao(self.gestora, revisao.pk)

        for acao in (confirmar_revisao, abandonar_revisao):
            with self.subTest(acao=acao.__name__):
                with self.assertRaisesMessage(
                    ErroDeNegocio, 'Esta Revisão não existe mais. Comece uma nova Importação.'
                ):
                    acao(self.gestora, revisao.pk)


class ConfirmacaoEmTransacaoUnicaTests(TesteTransacionalComArquivosEnviados):
    def test_se_uma_oferta_falha_ao_confirmar_nada_fica_salvo_e_a_revisao_continua_em_andamento(self):
        gestora = criar_gestor('gestora')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        cartoes = [
            CartaoFicticio('1001', 'Balde Ficticio', '7,50'),
            CartaoFicticio('1002', 'Rodo Ficticio', '-5,00'),  # o banco recusa preço negativo
        ]
        revisao = iniciar_importacao(gestora, fornecedor, arquivo_enviado(catalogo_ficticio_layout_a(cartoes)))

        with self.assertRaises(IntegrityError):
            confirmar_revisao(gestora, revisao.pk)

        self.assertEqual(list(listar_catalogos_do_fornecedor(gestora, fornecedor)), [])
        # Ainda não há caso de uso que liste Ofertas (a busca é do ticket 09): olho o modelo direto.
        self.assertFalse(Oferta.objects.exists())
        self.assertEqual([r.pk for r in listar_revisoes_em_andamento(gestora)], [revisao.pk])
