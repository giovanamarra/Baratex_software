"""Buscar Ofertas vigentes (ticket 09; ADR-0005, ADR-0007)."""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import confirmar_revisao, iniciar_importacao, informar_condicoes_do_catalogo

DIA_01 = date(2026, 3, 1)
DIA_15 = date(2026, 3, 15)


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

    def importar(self, cartoes, dia, fornecedor=None, desconto='0', gestor=None):
        """Importa e confirma um Catálogo fictício do Layout A, no dia dado."""
        gestor = gestor or self.gestora
        arquivo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes))
        revisao = iniciar_importacao(gestor, fornecedor or self.alfa, arquivo, hoje=dia)
        informar_condicoes_do_catalogo(gestor, revisao.pk, desconto)
        return confirmar_revisao(gestor, revisao.pk, hoje=dia)

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

    def test_a_busca_padrao_mostra_so_a_oferta_do_catalogo_mais_recente_do_fornecedor(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], DIA_15)

        achadas = self.buscar('1001')

        self.assertEqual(
            [(o.preco_unitario, o.catalogo.data) for o in achadas],
            [(Decimal('11.00'), DIA_15)],
        )

    def test_sem_so_vigentes_mostra_tambem_as_ofertas_antigas(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,00')], DIA_01)
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], DIA_15)

        achadas = self.buscar('1001', so_vigentes=False)

        self.assertEqual(
            sorted((o.preco_unitario, o.catalogo.data) for o in achadas),
            [(Decimal('10.00'), DIA_01), (Decimal('11.00'), DIA_15)],
        )

    def test_no_mesmo_dia_vale_a_oferta_de_menor_preco_unitario_e_nao_a_de_menor_preco_impresso(self):
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '10,50')], DIA_15, desconto='0')
        self.importar([CartaoFicticio('1001', 'Balde Ficticio', '11,00')], DIA_15, desconto='10')

        achadas = self.buscar('1001')

        self.assertEqual([o.preco_unitario for o in achadas], [Decimal('9.90')])

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
