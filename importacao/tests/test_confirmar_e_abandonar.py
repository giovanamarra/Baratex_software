from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_catalogos_do_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, resumo
from importacao.casos_de_uso import confirmar_revisao, iniciar_importacao


class ConfirmarRevisaoTests(TesteComArquivosEnviados):
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
