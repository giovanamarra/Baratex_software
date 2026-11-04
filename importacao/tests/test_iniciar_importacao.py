from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor
from comparador.erros import AcessoNegado, ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import (
    CartaoFicticio,
    catalogo_ficticio_layout_a,
    pdf_ficticio_com_texto,
)
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, resumo
from importacao.casos_de_uso import iniciar_importacao, listar_revisoes_em_andamento, obter_revisao


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

    def test_revisao_em_andamento_buscada_de_novo_traz_as_mesmas_ofertas(self):
        cartoes = [
            CartaoFicticio('1001', 'Balde Ficticio', '7,50', '6'),
            CartaoFicticio('1002', 'Rodo Ficticio', '11,00', '12'),
        ]
        revisao = iniciar_importacao(
            self.gestora, self.fornecedor, arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        )

        recarregada = obter_revisao(self.gestora, revisao.pk)

        self.assertEqual(
            [resumo(oferta) for oferta in recarregada.ofertas_propostas()],
            [
                ('1001', 'Balde Ficticio', Decimal('7.50'), 6, 'grade de cartões'),
                ('1002', 'Rodo Ficticio', Decimal('11.00'), 12, 'grade de cartões'),
            ],
        )

    def test_gestora_ve_so_as_proprias_revisoes_em_andamento(self):
        outro_gestor = criar_gestor('outro-gestor')
        primeira = self.iniciar_com_um_cartao(self.gestora)
        segunda = self.iniciar_com_um_cartao(self.gestora)
        self.iniciar_com_um_cartao(outro_gestor)

        revisoes = listar_revisoes_em_andamento(self.gestora)

        self.assertCountEqual([revisao.pk for revisao in revisoes], [primeira.pk, segunda.pk])

    def test_abrir_a_revisao_de_outro_gestor_e_recusado(self):
        revisao_da_gestora = self.iniciar_com_um_cartao(self.gestora)
        outro_gestor = criar_gestor('outro-gestor')

        with self.assertRaisesMessage(AcessoNegado, 'Esta Revisão é de outro Gestor.'):
            obter_revisao(outro_gestor, revisao_da_gestora.pk)

    def test_arquivo_enviado_fica_guardado_com_a_revisao(self):
        conteudo = catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio')])
        revisao = iniciar_importacao(self.gestora, self.fornecedor, arquivo_enviado(conteudo))

        guardada = obter_revisao(self.gestora, revisao.pk)

        with guardada.arquivo.open('rb') as arquivo:
            self.assertEqual(arquivo.read(), conteudo)

    def iniciar_com_um_cartao(self, gestor):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio')]))
        return iniciar_importacao(gestor, self.fornecedor, catalogo)


class ImportacaoRecusadaTests(TesteComArquivosEnviados):
    """Cada recusa tem mensagem em português e não cria Revisão."""

    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')
        self.catalogo_valido = arquivo_enviado(
            catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio')])
        )

    def assertRecusada(self, mensagem, fornecedor, arquivo):
        with self.assertRaisesMessage(ErroDeNegocio, mensagem):
            iniciar_importacao(self.gestora, fornecedor, arquivo)
        self.assertEqual(list(listar_revisoes_em_andamento(self.gestora)), [])

    def test_importacao_sem_fornecedor_e_recusada(self):
        self.assertRecusada('Escolha o Fornecedor do Catálogo.', None, self.catalogo_valido)

    def test_importacao_sem_arquivo_e_recusada(self):
        self.assertRecusada('Escolha o arquivo do Catálogo.', self.fornecedor, None)

    def test_documento_sem_nenhum_preco_e_recusado(self):
        sem_precos = catalogo_ficticio_layout_a(
            [CartaoFicticio('1001', 'Balde Ficticio', preco=None), CartaoFicticio('1002', 'Rodo Ficticio', preco=None)]
        )

        self.assertRecusada(
            'Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.',
            self.fornecedor,
            arquivo_enviado(sem_precos),
        )

    def test_arquivo_que_nao_abre_e_recusado(self):
        self.assertRecusada(
            'Não consegui abrir este arquivo. Ele pode estar corrompido: peça ao Fornecedor que envie de novo.',
            self.fornecedor,
            arquivo_enviado(b'%PDF-1.4 bytes quebrados, sem estrutura de PDF', nome='catalogo.pdf'),
        )

    def test_pdf_de_layout_desconhecido_e_recusado_por_enquanto(self):
        lista_de_precos = pdf_ficticio_com_texto(
            ['COD  DESCRICAO  PRECO', '1001  Balde Ficticio  R$ 7,50', '1002  Rodo Ficticio  R$ 11,00']
        )

        self.assertRecusada(
            'Não reconheci o Layout deste PDF. Por enquanto, só Catálogos em grade de cartões '
            'de Layouts conhecidos podem ser importados.',
            self.fornecedor,
            arquivo_enviado(lista_de_precos),
        )

    def test_excel_imagem_ou_outro_formato_e_recusado_por_enquanto(self):
        outros_formatos = {
            'catalogo.xlsx': b'PK\x03\x04 planilha ficticia',
            'pagina.png': b'\x89PNG\r\n\x1a\n imagem ficticia',
            'pagina.jpg': b'\xff\xd8\xff\xe0 imagem ficticia',
            'pedido.docx': b'PK\x03\x04 documento ficticio',
            'excel-renomeado.pdf': b'PK\x03\x04 planilha ficticia com nome de PDF',
        }
        for nome, conteudo in outros_formatos.items():
            with self.subTest(arquivo=nome):
                self.assertRecusada(
                    'Por enquanto, só Catálogos em PDF de grade de cartões podem ser importados.',
                    self.fornecedor,
                    arquivo_enviado(conteudo, nome=nome),
                )
