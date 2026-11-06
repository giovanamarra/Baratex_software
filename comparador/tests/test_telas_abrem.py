"""Cada tela principal abre e mostra o essencial, para pegar template quebrado (spec, Testing Decisions).

Os casos de uso já são testados pelo seam principal; aqui só se verifica que a página renderiza com
dados de teste e mostra um texto-chave.
"""

import re
from datetime import date
from decimal import Decimal
from urllib.parse import urlencode

from django.urls import reverse

from catalogos.casos_de_uso import (
    cadastrar_fornecedor,
    definir_conteudo,
    definir_teto,
    listar_catalogos_do_fornecedor,
    obter_teto,
)
from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor, criar_loja
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, informar_data_de_hoje
from importacao.casos_de_uso import (
    confirmar_revisao,
    informar_condicoes_do_catalogo,
    informar_data_do_catalogo,
    iniciar_importacao,
)


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
        informar_data_de_hoje(self.gestora, revisao.pk)
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
                CartaoFicticio('1001', 'Balde Ficticio Outra Secao', '9,50'),  # código repetido (ticket 32)
            ],
            rodape='Frete gratis acima de R$500,00',  # um preço que não vira Oferta
        )

        resposta = self.client.get(reverse('revisao', kwargs={'pk': revisao.pk}))

        for texto in [
            'Balde Ficticio', 'sem preço', 'sem Caixa', 'fora do padrão', 'unidade ambígua',
            'Sugestão: Conteúdo 3', 'Aceitar', 'Manter 1',
            'Preços no arquivo: <strong>10</strong> · Ofertas extraídas: <strong>9</strong>',
            'Falta 1 Oferta: confira o arquivo.',
            # Data do Catálogo junto do desconto, vazia, com o atalho do dia em que a Importação começou (ticket 31)
            'Data do Catálogo', 'É de hoje (02/03/2026)',
            'Código repetido (2 Ofertas)', 'código repetido',
        ]:
            with self.subTest(texto=texto):
                self.assertContains(resposta, texto)

    def test_atalho_e_de_hoje_e_o_campo_da_data_gravam_a_data_do_catalogo_pelo_caso_de_uso(self):
        revisao = self.importar([CartaoFicticio('1001', 'Balde Ficticio', '9,90')])  # Importação de 02/03/2026
        url = reverse('informar_data_do_catalogo', kwargs={'pk': revisao.pk})
        pagina = self.client.get(reverse('revisao', kwargs={'pk': revisao.pk}))
        self.assertContains(pagina, f'action="{url}"')
        self.assertContains(pagina, '<input type="hidden" name="data" value="02/03/2026">', html=False)

        self.assertContains(pagina, 'Data do Catálogo: <strong>não informada</strong>')

        atalho = self.client.post(url, {'data': '02/03/2026'}, follow=True)  # o que o botão do atalho envia
        self.assertContains(atalho, 'Data do Catálogo: <strong>02/03/2026</strong>')

        digitada = self.client.post(url, {'data': '10/2025'}, follow=True)
        self.assertContains(digitada, 'Data do Catálogo: <strong>10/2025</strong>')

        recusada = self.client.post(url, {'data': '31/02/2026'}, follow=True)
        self.assertContains(recusada, 'Informe a data do Catálogo como dia/mês/ano ou mês/ano')
        self.assertContains(recusada, 'Data do Catálogo: <strong>10/2025</strong>')  # a recusa não apaga a anterior

    def test_catalogos_do_fornecedor_abre_e_mostra_a_data_do_catalogo_e_o_dia_da_importacao(self):
        revisao = self.importar([CartaoFicticio('1001', 'Balde Ficticio', '9,90')])  # Importação de 02/03/2026
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_do_catalogo(self.gestora, revisao.pk, '10/2025', hoje=date(2026, 3, 2))
        confirmar_revisao(self.gestora, revisao.pk)

        resposta = self.client.get(reverse('catalogos_do_fornecedor', kwargs={'pk': self.fornecedor.pk}))

        for texto in ['Data do Catálogo', 'Importado em', '<td class="numero-tabular">10/2025</td>', '02/03/2026']:
            with self.subTest(texto=texto):
                self.assertContains(resposta, texto)

    def test_confirmar_pela_tela_mostra_a_data_do_catalogo_como_foi_informada_e_nao_o_dia_da_importacao(self):
        revisao = self.importar([CartaoFicticio('1001', 'Balde Ficticio', '9,90')])  # Importação de 02/03/2026
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_do_catalogo(self.gestora, revisao.pk, '10/2025', hoje=date(2026, 3, 2))

        confirmada = self.client.post(reverse('confirmar_revisao', kwargs={'pk': revisao.pk}), follow=True)
        catalogo = listar_catalogos_do_fornecedor(self.gestora, self.fornecedor).get()
        paginas = {
            'mensagem da confirmação': (confirmada, 'Revisão confirmada: Catálogo de 10/2025 salvo.'),
            'página do Catálogo': (self.client.get(reverse('catalogo', kwargs={'pk': catalogo.pk})), 'Fornecedor Alfa, 10/2025'),
            'Revisão confirmada': (
                self.client.get(reverse('revisao', kwargs={'pk': revisao.pk})), 'O Catálogo de 10/2025 já foi salvo.'
            ),
        }

        for pagina, (resposta, texto) in paginas.items():
            with self.subTest(pagina=pagina):
                self.assertContains(resposta, texto)

    def test_ofertas_de_um_catalogo_abre_e_mostra_o_preco_unitario_e_o_botao_corrigir_a_data(self):
        catalogo = self.catalogo_confirmado()

        resposta = self.client.get(reverse('catalogo', kwargs={'pk': catalogo.pk}))

        self.assertContains(resposta, 'Balde Ficticio')
        self.assertContains(resposta, 'R$ 9,90')
        corrigir = reverse('corrigir_data_do_catalogo', kwargs={'pk': catalogo.pk})
        self.assertContains(resposta, f'<a class="botao botao--secundario" href="{corrigir}">Corrigir a data</a>', html=True)

    def test_corrigir_a_data_abre_com_a_data_atual_o_campo_e_o_botao_ver_o_impacto(self):
        catalogo = self.catalogo_confirmado()  # data do Catálogo 02/03/2026

        resposta = self.client.get(reverse('corrigir_data_do_catalogo', kwargs={'pk': catalogo.pk}))

        self.assertContains(resposta, 'Data atual: <strong>02/03/2026</strong>')
        self.assertContains(resposta, '<input id="data" name="data" type="text" inputmode="numeric" value="" placeholder="15/10/2026 ou 10/2026">', html=True)
        self.assertContains(resposta, '<button class="botao botao--primario" type="submit">Ver o impacto</button>', html=True)

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
        outro = cadastrar_fornecedor(self.gestora, 'Fornecedor Beta')
        revisao = iniciar_importacao(  # só mês e ano, como a gestora informou
            self.gestora, outro, arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('2001', 'Balde Grande', '12,00')])),
            hoje=date(2026, 3, 2),
        )
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_do_catalogo(self.gestora, revisao.pk, '10/2025', hoje=date(2026, 3, 2))
        confirmar_revisao(self.gestora, revisao.pk)

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'balde'})

        for texto in [
            'Mostrar também Ofertas antigas', 'Todos os Fornecedores', 'Fornecedor Alfa', 'Balde Ficticio',
            'R$ 9,90', '02/03/2026', 'Definir Conteúdo', '>10/2025</a>',
        ]:
            with self.subTest(texto=texto):
                self.assertContains(resposta, texto)
        self.assertContains(resposta, f'href="{reverse("buscar_ofertas")}"')  # "Buscar" na barra de navegação

    def confirmar(self, cartoes, hoje=date(2026, 3, 2), fornecedor=None):
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(self.gestora, fornecedor or self.fornecedor, arquivo, hoje=hoje)
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)
        return confirmar_revisao(self.gestora, revisao.pk)

    def test_buscar_com_ofertas_antigas_marcado_mostra_tambem_as_antigas(self):
        self.confirmar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], hoje=date(2026, 3, 1))
        self.confirmar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], hoje=date(2026, 3, 15))

        so_vigentes = self.client.get(reverse('buscar_ofertas'), {'texto': 'balde'})
        com_antigas = self.client.get(reverse('buscar_ofertas'), {'texto': 'balde', 'antigas': '1'})

        self.assertContains(so_vigentes, 'R$ 11,00')
        self.assertNotContains(so_vigentes, 'R$ 10,00')
        self.assertContains(com_antigas, 'R$ 11,00')
        self.assertContains(com_antigas, 'R$ 10,00')

    def test_buscar_com_um_fornecedor_escolhido_mostra_so_as_ofertas_dele(self):
        beta = cadastrar_fornecedor(self.gestora, 'Fornecedor Beta')
        self.confirmar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')])
        self.confirmar([CartaoFicticio('1001', 'Balde Ficticio', '9,00')], fornecedor=beta)

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'balde', 'fornecedor': beta.pk})

        self.assertContains(resposta, 'R$ 9,00')
        self.assertNotContains(resposta, 'R$ 10,00')

    def test_buscar_com_um_fornecedor_que_nao_existe_nao_encontra_nenhuma_oferta(self):
        self.catalogo_confirmado()

        for fornecedor in [str(self.fornecedor.pk + 1000), 'abc']:
            for texto in ['balde', '']:
                with self.subTest(fornecedor=fornecedor, texto=texto):
                    resposta = self.client.get(reverse('buscar_ofertas'), {'texto': texto, 'fornecedor': fornecedor})

                    self.assertContains(resposta, 'Nenhuma Oferta encontrada.')
                    self.assertNotContains(resposta, 'Balde Ficticio')

    def test_buscar_mostra_o_formulario_preenchido_com_os_filtros_da_busca(self):
        self.catalogo_confirmado()

        resposta = self.client.get(
            reverse('buscar_ofertas'), {'texto': 'balde', 'fornecedor': self.fornecedor.pk, 'antigas': '1'}
        )

        self.assertContains(resposta, '<input id="texto" name="texto" type="text" value="balde" autofocus>', html=True)
        self.assertContains(
            resposta, f'<option value="{self.fornecedor.pk}" selected>Fornecedor Alfa</option>', html=True
        )
        self.assertContains(resposta, '<input id="antigas" name="antigas" type="checkbox" value="1" checked>', html=True)

    def test_buscar_com_exatamente_200_resultados_nao_avisa_do_limite(self):
        self.confirmar([CartaoFicticio(str(c), f'Item Ficticio {c}', '9,90') for c in range(1000, 1200)])

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'ficticio'})

        self.assertContains(resposta, 'Item Ficticio 1199')
        self.assertNotContains(resposta, 'Refine a busca')

    def test_buscar_com_mais_de_200_resultados_avisa_para_refinar_a_busca(self):
        revisao = self.importar([CartaoFicticio(str(c), f'Item Ficticio {c}', '9,90') for c in range(1000, 1201)])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)
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


    def link_de_definir_conteudo(self, resposta):
        return re.search(r'href="([^"]*/conteudo/[^"]*)"', resposta.content.decode()).group(1)

    def test_definir_conteudo_aberto_a_partir_da_busca_volta_para_a_busca_com_os_mesmos_filtros(self):
        self.catalogo_confirmado()
        busca = reverse('buscar_ofertas') + f'?texto=balde&fornecedor={self.fornecedor.pk}&antigas=1'
        link = self.link_de_definir_conteudo(self.client.get(busca))

        self.client.get(link)
        resposta = self.client.post(link, {'conteudo': '3'})

        self.assertRedirects(resposta, busca)

    def test_definir_conteudo_aberto_a_partir_do_catalogo_volta_para_o_catalogo(self):
        catalogo = self.catalogo_confirmado()
        link = self.link_de_definir_conteudo(self.client.get(reverse('catalogo', kwargs={'pk': catalogo.pk})))

        resposta = self.client.post(link, {'conteudo': '3'})

        self.assertRedirects(resposta, reverse('catalogo', kwargs={'pk': catalogo.pk}))

    def test_definir_conteudo_ignora_um_endereco_de_volta_que_nao_e_do_sistema(self):
        catalogo = self.catalogo_confirmado()
        oferta = catalogo.ofertas()[0]
        url = reverse('definir_conteudo', kwargs={'pk': oferta.pk})

        for voltar in ['https://exemplo.invalido/', '//exemplo.invalido/', '/\\exemplo.invalido/',
                       '///exemplo.invalido/', 'javascript:alert(1)']:
            with self.subTest(voltar=voltar):
                resposta = self.client.post(url, {'conteudo': '3'}, QUERY_STRING=urlencode({'voltar': voltar}))

                self.assertRedirects(resposta, reverse('catalogo', kwargs={'pk': catalogo.pk}))

    def test_definir_conteudo_aberto_a_partir_da_busca_oferece_voltar_a_busca(self):
        self.catalogo_confirmado()
        busca = reverse('buscar_ofertas') + '?texto=balde'
        link = self.link_de_definir_conteudo(self.client.get(busca))

        resposta = self.client.get(link)

        self.assertContains(resposta, f'<a class="botao botao--secundario" href="{busca}">Voltar à busca</a>', html=True)
        self.assertNotContains(resposta, 'Voltar ao Catálogo')

    def test_teto_de_compra_abre_e_mostra_o_valor_atual_e_o_campo_para_defini_lo(self):
        sem_teto = self.client.get(reverse('teto_de_compra'))
        definir_teto(self.gestora, '5,00')

        com_teto = self.client.get(reverse('teto_de_compra'))

        self.assertContains(sem_teto, 'Nenhum Teto de compra definido')
        self.assertContains(com_teto, 'Teto de compra atual: <strong>R$ 5,00</strong>')
        self.assertContains(com_teto, 'name="teto"')

    def test_teto_de_compra_salva_pelo_caso_de_uso_e_mostra_o_erro_de_um_valor_recusado(self):
        salvo = self.client.post(reverse('teto_de_compra'), {'teto': '5,00'})
        recusado = self.client.post(reverse('teto_de_compra'), {'teto': '0'})

        self.assertRedirects(salvo, reverse('teto_de_compra'))
        self.assertContains(recusado, 'O Teto de compra precisa ser maior que zero.')
        self.assertContains(recusado, 'Teto de compra atual: <strong>R$ 5,00</strong>')
        self.assertEqual(obter_teto(self.gestora), Decimal('5.00'))

    def test_buscar_destaca_com_o_texto_acima_do_teto_so_a_oferta_acima_do_teto(self):
        revisao = self.importar([
            CartaoFicticio('1001', 'Balde Ficticio', '9,90'),
            CartaoFicticio('1002', 'Rodo Ficticio', '4,00'),
        ])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)
        confirmar_revisao(self.gestora, revisao.pk)
        definir_teto(self.gestora, '5,00')

        resposta = self.client.get(reverse('buscar_ofertas'), {'texto': 'ficticio'})

        self.assertContains(resposta, 'acima do Teto', count=1)
        linha_do_balde = re.search(r'<tr[^>]*>(?:(?!</tr>).)*Balde Ficticio.*?</tr>', resposta.content.decode(), re.S)
        self.assertIn('linha--alerta', linha_do_balde.group(0))
        self.assertIn('acima do Teto', linha_do_balde.group(0))

    def test_catalogo_confirmado_destaca_com_o_texto_acima_do_teto_so_a_oferta_acima_do_teto(self):
        catalogo = self.confirmar([
            CartaoFicticio('1001', 'Balde Ficticio', '9,90'),
            CartaoFicticio('1002', 'Rodo Ficticio', '4,00'),
        ])
        definir_teto(self.gestora, '5,00')

        resposta = self.client.get(reverse('catalogo', kwargs={'pk': catalogo.pk}))

        self.assertContains(resposta, 'acima do Teto', count=1)
        linha_do_balde = re.search(r'<tr[^>]*>(?:(?!</tr>).)*Balde Ficticio.*?</tr>', resposta.content.decode(), re.S)
        self.assertIn('linha--alerta', linha_do_balde.group(0))
        self.assertIn('acima do Teto', linha_do_balde.group(0))

    def test_revisao_destaca_com_o_texto_acima_do_teto_so_a_oferta_acima_do_teto(self):
        revisao = self.importar([
            CartaoFicticio('1001', 'Balde Ficticio', '9,90'),
            CartaoFicticio('1002', 'Rodo Ficticio', '4,00'),
        ])
        definir_teto(self.gestora, '5,00')

        resposta = self.client.get(reverse('revisao', kwargs={'pk': revisao.pk}))

        self.assertContains(resposta, 'acima do Teto', count=1)
        linha_do_balde = re.search(r'<tr[^>]*>(?:(?!</tr>).)*Balde Ficticio.*?</tr>', resposta.content.decode(), re.S)
        self.assertIn('linha--alerta', linha_do_balde.group(0))
        self.assertIn('acima do Teto', linha_do_balde.group(0))
