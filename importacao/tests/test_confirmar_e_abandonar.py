from catalogos.casos_de_uso import cadastrar_fornecedor, listar_catalogos_do_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao


class ConfirmarRevisaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def iniciar(self, cartoes=None):
        cartoes = cartoes or [CartaoFicticio('1001', 'Balde Ficticio')]
        return iniciar_importacao(
            self.gestora, self.fornecedor, arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        )

    def test_antes_de_confirmar_o_fornecedor_continua_sem_catalogos(self):
        self.iniciar()

        self.assertEqual(list(listar_catalogos_do_fornecedor(self.gestora, self.fornecedor)), [])
