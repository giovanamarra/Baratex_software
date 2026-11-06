"""Buscar Ofertas vigentes (tickets 09 e 31; ADR-0005, ADR-0007, ADR-0009)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor, definir_conteudo
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, cartoes_com_o_segundo_na_pagina_2, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, corrigir, informar_data_de_hoje
from importacao.casos_de_uso import (
    adicionar_oferta_proposta,
    confirmar_revisao,
    iniciar_importacao,
    informar_condicoes_do_catalogo,
    informar_data_do_catalogo,
    obter_revisao,
)

DIA_01 = date(2026, 3, 1)
DIA_15 = date(2026, 3, 15)
HOJE = date(2026, 11, 5)


def achado(oferta):
    return (
        oferta.codigo,
        oferta.descricao,
        oferta.preco_unitario,
        oferta.caixa,
        oferta.catalogo.fornecedor.nome,
        oferta.catalogo.data,
    )


class BuscarOfertasTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.alfa = cadastrar_fornecedor(self.gestora, 'Alfa')
        self.beta = cadastrar_fornecedor(self.gestora, 'Beta')

    def importar(self, cartoes, data, fornecedor=None, desconto='0', gestor=None, hoje=HOJE):
        """Importa e confirma um Catálogo fictício do Layout A com a data do Catálogo dada, como a gestora
        digita ("15/10/2026", "10/2026") ou como date. `hoje` é o dia da Importação, separado da data."""
        gestor = gestor or self.gestora
        if isinstance(data, date):
            data = f'{data:%d/%m/%Y}'
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(gestor, fornecedor or self.alfa, arquivo, hoje=hoje)
        informar_condicoes_do_catalogo(gestor, revisao.pk, desconto)
        informar_data_do_catalogo(gestor, revisao.pk, data, hoje=hoje)
        return confirmar_revisao(gestor, revisao.pk, hoje=hoje)

    def buscar(self, texto='', **filtros):
        return buscar_ofertas(self.gestora, texto, **filtros).ofertas

    def test_acha_pelo_codigo_e_mostra_codigo_descricao_preco_unitario_caixa_fornecedor_e_data(self):
        self.importar([
            CartaoFicticio('1001', 'Balde Ficticio', '9,90', caixa='24'),
            CartaoFicticio('1002', 'Rodo Ficticio', '12,00'),
        ], DIA_01)

        achadas = self.buscar('1001')

        self.assertEqual(
            [achado(o) for o in achadas],
            [('1001', 'Balde Ficticio', Decimal('9.90'), 24, 'Alfa', DIA_01)],
        )

    def test_acha_por_trecho_da_descricao_sem_diferenciar_maiusculas_nem_acentos(self):
        self.importar([
            CartaoFicticio('1001', 'Cesta Plástica Média', '9,90'),
            CartaoFicticio('1002', 'Vassoura Ficticia', '12,00'),
            CartaoFicticio('1003', 'Lixeira Plastica Pequena', '8,00'),
        ], DIA_01)

        casos = [
            ('plastica', ['1001', '1003']),
            ('PLÁSTICA', ['1001', '1003']),
            ('Plástica', ['1001', '1003']),
            ('média', ['1001']),
            ('MEDIA', ['1001']),
        ]
        for digitado, esperado in casos:
            with self.subTest(digitado=digitado):
                self.assertEqual(sorted(o.codigo for o in self.buscar(digitado)), esperado)

    def test_vale_a_oferta_do_catalogo_de_data_mais_recente_mesmo_com_o_preco_maior(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], DIA_15)

        achadas = self.buscar('1001')

        self.assertEqual(
            [(o.preco_unitario, o.catalogo.data) for o in achadas],
            [(Decimal('11.00'), DIA_15)],
        )

    def test_catalogo_antigo_importado_depois_nao_derruba_a_oferta_do_catalogo_mais_recente(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], '15/10/2026', hoje=date(2026, 10, 16))
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], '01/09/2026', hoje=date(2026, 10, 20))

        achadas = self.buscar('1001')

        self.assertEqual([(o.preco_unitario, o.catalogo.data_exibida) for o in achadas], [(Decimal('11.00'), '15/10/2026')])

    def test_a_substituicao_e_codigo_a_codigo_e_o_codigo_que_falta_no_catalogo_novo_continua_vigente(self):
        self.importar([
            CartaoFicticio('1001', 'Balde Ficticio', '10,00'),
            CartaoFicticio('1002', 'Rodo Ficticio', '7,00'),
        ], '01/10/2026')
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], '15/10/2026')

        achadas = self.buscar('ficticio')

        self.assertEqual(
            [(o.codigo, o.preco_unitario, o.catalogo.data_exibida) for o in achadas],
            [('1001', Decimal('11.00'), '15/10/2026'), ('1002', Decimal('7.00'), '01/10/2026')],
        )

    def test_sem_so_vigentes_mostra_tambem_as_ofertas_antigas(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], DIA_15)

        achadas = self.buscar('1001', so_vigentes=False)

        self.assertEqual(
            sorted((o.preco_unitario, o.catalogo.data) for o in achadas),
            [(Decimal('10.00'), DIA_01), (Decimal('11.00'), DIA_15)],
        )

    def test_na_mesma_data_vale_o_catalogo_confirmado_por_ultimo_mesmo_mais_caro(self):
        # Até o ticket 31, na mesma data valia o menor Preço unitário (9,90). Agora vale o confirmado por último
        # (ADR-0009, regra 2), e a busca padrão devolve uma Oferta só para o código.
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], '15/10/2026', desconto='10')  # 9,90
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,50')], '15/10/2026', desconto='0')

        achadas = self.buscar('1001')

        self.assertEqual([o.preco_unitario for o in achadas], [Decimal('10.50')])

    def test_na_mesma_data_e_com_o_mesmo_preco_vale_o_catalogo_confirmado_por_ultimo(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00', caixa='6')], '15/10/2026')
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00', caixa='12')], '15/10/2026')

        achadas = self.buscar('1001')

        self.assertEqual([(o.preco_unitario, o.caixa) for o in achadas], [(Decimal('10.00'), 12)])

    def test_codigo_repetido_no_mesmo_catalogo_vale_a_oferta_de_menor_preco_unitario(self):
        # ADR-0009, item 3: a mais barata está na página 2, depois da mais cara.
        self.importar(cartoes_com_o_segundo_na_pagina_2(
            CartaoFicticio('1001', 'Balde Ficticio Secao A', '12,90'),
            CartaoFicticio('1001', 'Balde Ficticio Secao B', '11,50'),
        ), '15/10/2026')

        achadas = self.buscar('1001')

        self.assertEqual([(o.descricao, o.preco_unitario) for o in achadas], [('Balde Ficticio Secao B', Decimal('11.50'))])

    def test_codigo_repetido_com_o_mesmo_preco_unitario_vale_a_que_aparece_primeiro_no_arquivo(self):
        self.importar(cartoes_com_o_segundo_na_pagina_2(
            CartaoFicticio('1001', 'Balde Ficticio', '10,00', caixa='6'),
            CartaoFicticio('1001', 'Balde Ficticio', '10,00', caixa='12'),
        ), '15/10/2026')

        achadas = self.buscar('1001')

        self.assertEqual([(o.preco_unitario, o.caixa) for o in achadas], [(Decimal('10.00'), 6)])

    def test_codigo_repetido_que_so_empata_no_preco_unitario_arredondado_vale_a_primeira_do_arquivo(self):
        # Com Conteúdo 12: 10,01 / 12 = 0,834 e 10,00 / 12 = 0,833; as duas dão 0,83.
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes_com_o_segundo_na_pagina_2(
            CartaoFicticio('1001', 'Balde Ficticio Secao A', '10,01'),
            CartaoFicticio('1001', 'Balde Ficticio Secao B', '10,00'),
        )))
        revisao = iniciar_importacao(self.gestora, self.alfa, arquivo, hoje=HOJE)
        corrigir(self.gestora, obter_revisao(self.gestora, revisao.pk).ofertas_propostas()[0], conteudo='12')
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_do_catalogo(self.gestora, revisao.pk, '15/10/2026', hoje=HOJE)
        confirmar_revisao(self.gestora, revisao.pk, hoje=HOJE)

        achadas = self.buscar('1001')

        self.assertEqual([(o.descricao, o.preco_unitario) for o in achadas], [('Balde Ficticio Secao A', Decimal('0.83'))])

    def test_codigo_repetido_que_so_empata_no_preco_unitario_com_o_desconto_vale_a_primeira_do_arquivo(self):
        # Com 50% de desconto: 0,02 dá 0,01 e 0,01 dá 0,005, que arredonda para 0,01 (meio centavo para cima).
        self.importar(cartoes_com_o_segundo_na_pagina_2(
            CartaoFicticio('1001', 'Balde Ficticio Secao A', '0,02'),
            CartaoFicticio('1001', 'Balde Ficticio Secao B', '0,01'),
        ), '15/10/2026', desconto='50')

        achadas = self.buscar('1001')

        self.assertEqual([(o.descricao, o.preco_unitario) for o in achadas], [('Balde Ficticio Secao A', Decimal('0.01'))])

    def test_so_mes_e_ano_e_mais_antigo_que_um_dia_do_mesmo_mes_depois_do_dia_1(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], '15/10/2026')
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], '10/2026')  # confirmado depois

        achadas = self.buscar('1001')

        self.assertEqual([(o.preco_unitario, o.catalogo.data_exibida) for o in achadas], [(Decimal('11.00'), '15/10/2026')])

    def test_so_mes_e_ano_tem_a_mesma_data_que_o_dia_1_e_vale_o_confirmado_por_ultimo(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], '10/2026')
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], '01/10/2026')

        achadas = self.buscar('1001')

        self.assertEqual([(o.preco_unitario, o.catalogo.data_exibida) for o in achadas], [(Decimal('10.00'), '01/10/2026')])

    def test_com_as_ofertas_antigas_a_ordem_e_do_catalogo_de_data_mais_recente_para_o_mais_antigo(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], '15/10/2026', hoje=date(2026, 10, 16))
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], '09/2026', hoje=date(2026, 10, 20))
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,50')], '01/10/2026', hoje=date(2026, 10, 18))

        achadas = self.buscar('1001', so_vigentes=False)

        self.assertEqual([o.catalogo.data_exibida for o in achadas], ['15/10/2026', '01/10/2026', '09/2026'])

    def test_o_filtro_por_fornecedor_mostra_so_as_ofertas_dele(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01, fornecedor=self.alfa)
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '9,00')], DIA_01, fornecedor=self.beta)

        com_filtro = self.buscar('1001', fornecedor=self.beta)
        sem_filtro = self.buscar('1001')

        self.assertEqual([(o.catalogo.fornecedor.nome, o.preco_unitario) for o in com_filtro], [('Beta', Decimal('9.00'))])
        self.assertEqual(
            sorted((o.catalogo.fornecedor.nome, o.preco_unitario) for o in sem_filtro),
            [('Alfa', Decimal('10.00')), ('Beta', Decimal('9.00'))],
        )

    def test_oferta_sem_produto_aparece_na_busca(self):
        # O Produto só nasce no ticket 12: aqui nenhuma Oferta está ligada a um.
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)

        achadas = self.buscar('balde')

        self.assertEqual([o.codigo for o in achadas], ['1001'])

    def test_catalogo_importado_por_outro_gestor_aparece_na_busca_de_quem_busca(self):
        gestor_b = criar_gestor('gestor-b')
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01, gestor=gestor_b)

        achadas = buscar_ofertas(self.gestora, '1001').ofertas

        self.assertEqual([(o.codigo, o.catalogo.gestor.get_username()) for o in achadas], [('1001', 'gestor-b')])

    def test_texto_vazio_sem_fornecedor_e_erro_e_com_fornecedor_lista_as_ofertas_dele(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01, fornecedor=self.alfa)
        self.importar([CartaoFicticio('2001', 'Rodo Ficticio', '9,00')], DIA_01, fornecedor=self.beta)

        for vazio in ['', '   ']:
            with self.subTest(texto=repr(vazio)):
                with self.assertRaises(ErroDeNegocio) as erro:
                    self.buscar(vazio)
                self.assertEqual(
                    erro.exception.mensagem,
                    'Digite um código ou parte da descrição, ou escolha um Fornecedor.',
                )
        self.assertEqual([o.codigo for o in self.buscar('', fornecedor=self.alfa)], ['1001'])

    def test_busca_sem_resultado_nao_e_erro_e_devolve_lista_vazia(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)

        self.assertEqual(self.buscar('inexistente'), [])

    def test_devolve_no_maximo_200_ofertas_e_o_total_de_ofertas_encontradas(self):
        self.importar(
            [CartaoFicticio(str(codigo), f'Item Ficticio {codigo}', '10,00') for codigo in range(1000, 1201)], DIA_01
        )

        resultado = buscar_ofertas(self.gestora, 'ficticio')

        self.assertEqual((len(resultado.ofertas), resultado.total), (200, 201))

    def test_com_menos_de_200_resultados_o_total_e_o_numero_de_ofertas_devolvidas(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00'), CartaoFicticio('1002', 'Rodo', '9,00')], DIA_01)

        resultado = buscar_ofertas(self.gestora, 'ficticio')

        self.assertEqual((len(resultado.ofertas), resultado.total), (1, 1))

    def test_oferta_adicionada_a_mao_ou_corrigida_na_revisao_e_achada_pelo_que_foi_confirmado(self):
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio', '10,00')]))
        revisao = iniciar_importacao(self.gestora, self.alfa, arquivo, hoje=DIA_01)
        balde = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()[0]
        corrigir(self.gestora, balde, descricao='Bacia Plástica')
        adicionar_oferta_proposta(
            self.gestora, revisao.pk, codigo='2001', descricao='Escova Ácida', preco_impresso='3,40', caixa='60'
        )
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        informar_data_de_hoje(self.gestora, revisao.pk)
        confirmar_revisao(self.gestora, revisao.pk, hoje=DIA_01)

        casos = [('plastica', ['1001']), ('ACIDA', ['2001']), ('balde', [])]
        for digitado, esperado in casos:
            with self.subTest(digitado=digitado):
                self.assertEqual([o.codigo for o in self.buscar(digitado)], esperado)

    def test_com_so_vigentes_o_total_conta_so_as_ofertas_vigentes(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], DIA_15)

        vigentes = buscar_ofertas(self.gestora, '1001')
        todas = buscar_ofertas(self.gestora, '1001', so_vigentes=False)

        self.assertEqual((vigentes.total, todas.total), (1, 2))

    def test_o_preco_unitario_do_resultado_usa_o_conteudo_e_o_desconto_do_catalogo(self):
        self.importar([CartaoFicticio('1001', 'Kit 3 Tesouras Ficticias', '9,00')], DIA_01, desconto='10')
        definir_conteudo(self.gestora, self.alfa, '1001', '3', hoje=DIA_15)

        achadas = self.buscar('tesouras')

        self.assertEqual([o.preco_unitario for o in achadas], [Decimal('2.70')])
