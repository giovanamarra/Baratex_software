from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao


def resumo(oferta):
    return (oferta.codigo, oferta.descricao, oferta.preco_impresso, oferta.caixa, oferta.caminho)


class IniciarImportacaoTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def test_catalogo_de_n_cartoes_gera_n_ofertas_propostas(self):
        cartoes = [
            CartaoFicticio('1001', 'Tesoura Ficticia Ponta Redonda', '1.234,56', '12'),
            CartaoFicticio('1002', 'Pote Ficticio 500ml', '9,90', '48', ipi='sem ipi'),
            *[CartaoFicticio(str(2001 + n), f'Caneca Ficticia {n}', '5,00') for n in range(21)],
        ]  # 23 cartões: 20 na primeira página e 3 na segunda
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))

        revisao = iniciar_importacao(self.gestora, self.fornecedor, catalogo)

        ofertas = revisao.ofertas_propostas()
        self.assertEqual([oferta.codigo for oferta in ofertas], [cartao.codigo for cartao in cartoes])
        self.assertEqual(
            [resumo(ofertas[0]), resumo(ofertas[1]), resumo(ofertas[-1])],
            [
                ('1001', 'Tesoura Ficticia Ponta Redonda', Decimal('1234.56'), 12, 'grade de cartões'),
                ('1002', 'Pote Ficticio 500ml', Decimal('9.90'), 48, 'grade de cartões'),
                ('2021', 'Caneca Ficticia 20', Decimal('5.00'), 24, 'grade de cartões'),
            ],
        )

    def test_cartao_com_preco_ou_caixa_mascarados_vira_oferta_sem_preco_ou_sem_caixa(self):
        cartoes = [
            CartaoFicticio('1001', 'Balde Ficticio', preco='***,**'),
            CartaoFicticio('1002', 'Vassoura Ficticia', caixa='***'),
        ]
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))

        revisao = iniciar_importacao(self.gestora, self.fornecedor, catalogo)

        self.assertEqual(
            [resumo(oferta) for oferta in revisao.ofertas_propostas()],
            [
                ('1001', 'Balde Ficticio', None, 24, 'grade de cartões'),
                ('1002', 'Vassoura Ficticia', Decimal('12.90'), None, 'grade de cartões'),
            ],
        )

    def test_fornecedor_da_revisao_e_o_escolhido_mesmo_com_outra_marca_no_pdf(self):
        cadastrar_fornecedor(self.gestora, 'Fornecedor Beta')
        catalogo = arquivo_enviado(
            catalogo_ficticio_layout_a(
                [CartaoFicticio('1001', 'Balde Ficticio')],
                rodape='Catálogo de Produtos Fornecedor Beta Marca Zeta',
            )
        )

        revisao = iniciar_importacao(self.gestora, self.fornecedor, catalogo)

        self.assertEqual(revisao.fornecedor.nome, 'Fornecedor Alfa')
