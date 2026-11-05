"""Cada tela principal abre e mostra o essencial, para pegar template quebrado (spec, Testing Decisions).

Os casos de uso já são testados pelo seam principal; aqui só se verifica que a página renderiza com
dados de teste e mostra um texto-chave.
"""

from datetime import date

from django.urls import reverse

from catalogos.casos_de_uso import cadastrar_fornecedor, definir_conteudo
from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor, criar_loja
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import confirmar_revisao, informar_condicoes_do_catalogo, iniciar_importacao


class TelasAbremTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        criar_loja(self.gestora, 'Loja Centro')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')
        self.client.login(username='gestora', password=SENHA_DE_TESTE)

    def importar(self, cartoes, hoje=date(2026, 3, 2), **opcoes_do_pdf):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes, **opcoes_do_pdf))
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo, hoje=hoje)

    def catalogo_confirmado(self):
        revisao = self.importar([CartaoFicticio('1001', 'Balde Ficticio', '9,90')])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        return confirmar_revisao(self.gestora, revisao.pk)

    def test_inicio_abre_e_mostra_as_lojas(self):
        resposta = self.client.get(reverse('inicio'))

        self.assertContains(resposta, 'Loja Centro')

    def test_fornecedores_abre_e_mostra_os_fornecedores(self):
        resposta = self.client.get(reverse('fornecedores'))

        self.assertContains(resposta, 'Fornecedor Alfa')

    def test_importar_catalogo_abre_e_mostra_as_revisoes_em_andamento(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio')])

        resposta = self.client.get(reverse('importar'))

        self.assertContains(resposta, 'Retomar')

    def test_revisao_abre_e_mostra_as_ofertas_com_cada_marca_e_a_contagem(self):
        revisao = self.importar(
            [
                CartaoFicticio('1001', 'Balde Ficticio', '9,90'),
                CartaoFicticio('1002', 'Rodo Ficticio', '***,**'),  # mascarado, como no real
                CartaoFicticio('1003', 'Pa Ficticia', '10,00', caixa='***'),
                CartaoFicticio('1004', 'Escova Ficticia', '11,00'),
                CartaoFicticio('1005', 'Esponja Ficticia', '12,00'),
                CartaoFicticio('1006', 'Lixeira Ficticia', '150,00'),
                CartaoFicticio('2001', 'Kit Tesouras Ficticias', '10,00'),
                CartaoFicticio('3001', 'Tesoura Ficticia C/3', '9,00'),
            ],
            rodape='Frete gratis acima de R$500,00',  # um preço que não vira Oferta
        )

        resposta = self.client.get(reverse('revisao', kwargs={'pk': revisao.pk}))

        for texto in [
            'Balde Ficticio', 'sem preço', 'sem Caixa', 'fora do padrão', 'unidade ambígua',
            'Sugestão: Conteúdo 3', 'Aceitar', 'Manter 1',
            'Preços no arquivo: <strong>9</strong> · Ofertas extraídas: <strong>8</strong>',
            'Falta 1 Oferta: confira o arquivo.',
        ]:
            with self.subTest(texto=texto):
                self.assertContains(resposta, texto)

    def test_catalogos_do_fornecedor_abre_e_mostra_a_data_do_catalogo(self):
        self.catalogo_confirmado()

        resposta = self.client.get(reverse('catalogos_do_fornecedor', kwargs={'pk': self.fornecedor.pk}))

        self.assertContains(resposta, '02/03/2026')

    def test_ofertas_de_um_catalogo_abre_e_mostra_o_preco_unitario(self):
        catalogo = self.catalogo_confirmado()

        resposta = self.client.get(reverse('catalogo', kwargs={'pk': catalogo.pk}))

        self.assertContains(resposta, 'Balde Ficticio')
        self.assertContains(resposta, 'R$ 9,90')

    def test_definir_conteudo_abre_e_mostra_o_aviso_antes_de_salvar(self):
        balde = self.catalogo_confirmado().ofertas()[0]

        resposta = self.client.get(reverse('definir_conteudo', kwargs={'pk': balde.pk}))

        self.assertContains(resposta, 'Isto muda o Preço unitário desta Oferta em todos os Catálogos do Fornecedor.')

    def test_historico_do_conteudo_abre_e_mostra_as_alteracoes(self):
        balde = self.catalogo_confirmado().ofertas()[0]
        definir_conteudo(self.gestora, self.fornecedor, '1001', '3', hoje=date(2026, 3, 4))

        resposta = self.client.get(reverse('historico_do_conteudo', kwargs={'pk': balde.pk}))

        self.assertContains(resposta, '04/03/2026')

    def test_buscar_abre_e_mostra_o_formulario_e_os_resultados_com_definir_conteudo(self):
        self.catalogo_confirmado()

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'balde'})

        for texto in [
            'Mostrar também Ofertas antigas', 'Todos os Fornecedores', 'Fornecedor Alfa', 'Balde Ficticio',
            'R$ 9,90', '02/03/2026', 'Definir Conteúdo',
        ]:
            with self.subTest(texto=texto):
                self.assertContains(resposta, texto)
        self.assertContains(resposta, f'href="{reverse("buscar_ofertas")}"')  # "Buscar" na barra de navegação

    def test_buscar_com_mais_de_200_resultados_avisa_para_refinar_a_busca(self):
        revisao = self.importar([CartaoFicticio(str(c), f'Item Ficticio {c}', '9,90') for c in range(1000, 1201)])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        confirmar_revisao(self.gestora, revisao.pk)

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'ficticio'})

        self.assertContains(resposta, 'Mostrando 200 de 201 Ofertas. Refine a busca.')

    def test_buscar_sem_resultado_diz_que_nenhuma_oferta_foi_encontrada(self):
        self.catalogo_confirmado()

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'inexistente'})

        self.assertContains(resposta, 'Nenhuma Oferta encontrada.')

    def test_buscar_sem_texto_e_sem_fornecedor_mostra_o_erro_em_portugues(self):
        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': ''})

        self.assertContains(resposta, 'Digite um código ou parte da descrição, ou escolha um Fornecedor.')
