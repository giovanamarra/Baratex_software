"""Marcas de conferência e contagem de preços na Revisão (ticket 08; ADR-0006).

As regras foram calibradas com os Catálogos reais; os números estão no ticket 08. Aqui, só dados inventados.
"""

from datetime import date
from decimal import Decimal

from catalogos.casos_de_uso import cadastrar_fornecedor, definir_conteudo, historico_do_conteudo
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado, corrigir
from importacao.casos_de_uso import (
    abandonar_revisao,
    aceitar_sugestao_de_conteudo,
    confirmar_revisao,
    informar_condicoes_do_catalogo,
    iniciar_importacao,
    manter_conteudo_1,
    obter_revisao,
)


def cartoes_com_precos(*precos):
    return [CartaoFicticio(str(1001 + i), f'Item Ficticio {i + 1}', preco) for i, preco in enumerate(precos)]


class MarcasDeConferenciaTests(TesteComArquivosEnviados):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.fornecedor = cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

    def importar(self, cartoes, rodape='Catálogo de Produtos Fornecedor Fictício'):
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a(cartoes, rodape=rodape))
        return iniciar_importacao(self.gestora, self.fornecedor, catalogo)

    def marcas(self, revisao):
        return {oferta.codigo: oferta.marcas for oferta in obter_revisao(self.gestora, revisao.pk).ofertas_propostas()}

    def test_preco_mais_de_10_vezes_a_mediana_ou_menos_de_um_decimo_dela_fica_fora_do_padrao(self):
        # Mediana 10,00: 150,00 passa de 10 vezes; 0,90 fica abaixo de um décimo.
        revisao = self.importar(cartoes_com_precos('9,00', '10,00', '10,00', '11,00', '12,00', '150,00', '0,90'))

        self.assertEqual(
            self.marcas(revisao),
            {
                '1001': [], '1002': [], '1003': [], '1004': [], '1005': [],
                '1006': ['fora do padrão'],
                '1007': ['fora do padrão'],
            },
        )

    def test_com_menos_de_5_ofertas_com_preco_nada_fica_fora_do_padrao(self):
        # 3 preços e 2 Ofertas sem preço: as sem preço não contam para o mínimo nem para a mediana.
        revisao = self.importar(cartoes_com_precos('9,00', '10,00', '150,00', '***,**', '***,**'))

        self.assertEqual(
            self.marcas(revisao),
            {'1001': [], '1002': [], '1003': [], '1004': ['sem preço'], '1005': ['sem preço']},
        )

    def test_descricao_com_kit_cj_conjunto_set_ou_par_como_palavra_inteira_fica_com_unidade_ambigua(self):
        descricoes = {
            '2001': 'Kit Tesouras Ficticias',
            '2002': 'cj panelas ficticias',  # minúsculas
            '2003': 'Conjunto Potes Ficticios',
            '2004': 'Set Copos Ficticios',
            '2005': 'Par Luvas Ficticias',
            '2006': 'Kít Escovas Ficticias',  # com acento
            '2007': 'Kitchenette Ficticia',  # KIT dentro de outra palavra
            '2008': 'Parafuso Ficticio',  # PAR dentro de outra palavra
            '2009': 'Jogo Tabuleiro Ficticio',  # JOGO saiu da lista na calibração (ticket 08)
        }
        revisao = self.importar([CartaoFicticio(codigo, descricao) for codigo, descricao in descricoes.items()])

        ambiguas = [codigo for codigo, marcas in self.marcas(revisao).items() if 'unidade ambígua' in marcas]
        self.assertEqual(ambiguas, ['2001', '2002', '2003', '2004', '2005', '2006'])

    def test_descricao_que_cita_quantidade_de_pecas_gera_sugestao_de_conteudo(self):
        descricoes = {
            '3001': 'Tesoura Ficticia C/3',
            '3002': 'Faca Ficticia COM 4 PEÇAS',
            '3003': 'Copo Ficticio 6 PÇS',
            '3004': 'Prato Ficticio 2 PCS',
            '3005': 'Pincel Ficticio 12 UNID',
            '3006': 'Balde Ficticio C/ Tampa',  # "com tampa": não é quantidade
            '3007': 'Rodo Ficticio 1 PC',  # 1 peça não muda nada
            '3008': 'Regua Ficticia 30 CM',
        }
        revisao = self.importar([CartaoFicticio(codigo, descricao) for codigo, descricao in descricoes.items()])

        self.assertEqual(
            self.sugestoes(revisao),
            {'3001': 3, '3002': 4, '3003': 6, '3004': 2, '3005': 12, '3006': None, '3007': None, '3008': None},
        )
        # Sugerir não muda o Conteúdo (história 42).
        self.assertEqual({o.conteudo for o in obter_revisao(self.gestora, revisao.pk).ofertas_propostas()}, {1})

    def test_sugestao_so_aparece_com_conteudo_1_e_sem_decisao_guardada_para_o_fornecedor_e_codigo(self):
        cartoes = [
            CartaoFicticio('3001', 'Tesoura Ficticia C/3'),
            CartaoFicticio('3002', 'Faca Ficticia C/4'),
            CartaoFicticio('3003', 'Copo Ficticio C/6'),
            CartaoFicticio('3004', 'Prato Ficticio 2 PCS'),
        ]
        primeira = self.importar(cartoes)
        informar_condicoes_do_catalogo(self.gestora, primeira.pk, '0')
        confirmar_revisao(self.gestora, primeira.pk)
        definir_conteudo(self.gestora, self.fornecedor, '3001', '3')  # decisão guardada: 3
        definir_conteudo(self.gestora, self.fornecedor, '3002', '4')
        definir_conteudo(self.gestora, self.fornecedor, '3002', '1')  # decisão guardada, de volta a 1

        seguinte = self.importar(cartoes)
        corrigir(self.gestora, obter_revisao(self.gestora, seguinte.pk).ofertas_propostas()[3], conteudo='2')

        # Só a 3003 continua sem decisão e com Conteúdo 1; a 3004 teve o Conteúdo definido nesta Revisão.
        self.assertEqual(self.sugestoes(seguinte), {'3001': None, '3002': None, '3003': 6, '3004': None})

    def test_aceitar_a_sugestao_define_o_conteudo_que_fica_guardado_ao_confirmar(self):
        revisao = self.importar([CartaoFicticio('3001', 'Tesoura Ficticia C/3', '9,00')])
        tesoura = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()[0]

        aceitar_sugestao_de_conteudo(self.gestora, tesoura.pk)
        aceitar_sugestao_de_conteudo(self.gestora, tesoura.pk)  # repetir o clique não desfaz nada

        aceita = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()[0]
        self.assertEqual((aceita.conteudo, aceita.preco_unitario, aceita.sugestao_de_conteudo), (3, Decimal('3.00'), None))
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        confirmar_revisao(self.gestora, revisao.pk)
        self.assertEqual(
            [(r.valor_anterior, r.valor_novo) for r in historico_do_conteudo(self.gestora, self.fornecedor, '3001')],
            [(1, 3)],
        )

    def test_a_revisao_conta_os_precos_no_arquivo_e_as_ofertas_extraidas_e_aponta_as_que_faltam(self):
        # O preço mascarado conta como preço no arquivo: vira Oferta sem preço (regra 4 da calibração).
        cartoes = [CartaoFicticio('1001', 'Balde Ficticio', '9,90'), CartaoFicticio('1002', 'Rodo Ficticio', '***,**')]
        completa = self.importar(cartoes)
        # Um preço fora dos cartões, que o leitor não transforma em Oferta.
        com_preco_solto = self.importar(cartoes, rodape='Frete gratis acima de R$500,00')

        self.assertEqual(self.contagem(completa), (2, 2, 0))
        self.assertEqual(self.contagem(com_preco_solto), (3, 2, 1))

    def test_as_marcas_sao_recalculadas_depois_de_cada_correcao(self):
        revisao = self.importar(cartoes_com_precos('9,00', '10,00', '10,00', '11,00', '12,00', '150,00'))
        ofertas = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()
        self.assertEqual((self.marcas(revisao)['1006'], self.marcas(revisao)['1001']), (['fora do padrão'], []))

        corrigir(self.gestora, ofertas[5], preco_impresso='15,00')  # erro de leitura corrigido
        corrigir(self.gestora, ofertas[0], preco_impresso='0,50')  # e o contrário: agora fora do padrão

        marcas = self.marcas(revisao)
        self.assertEqual((marcas['1006'], marcas['1001']), ([], ['fora do padrão']))

    def test_fora_do_padrao_ambigua_e_sugestao_nao_impedem_a_confirmacao_mas_sem_preco_continua_impedindo(self):
        cartoes = [
            *cartoes_com_precos('9,00', '10,00', '10,00', '11,00', '12,00', '150,00'),  # 1006: fora do padrão
            CartaoFicticio('2001', 'Kit Tesouras Ficticias'),  # unidade ambígua
            CartaoFicticio('3001', 'Tesoura Ficticia C/3'),  # sugestão de Conteúdo
        ]
        sem_preco = self.importar([*cartoes, CartaoFicticio('1003', 'Pa Ficticia', '***,**')])
        marcadas = self.importar(cartoes)
        for revisao in (sem_preco, marcadas):
            informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')

        with self.assertRaisesMessage(
            ErroDeNegocio, 'Informe um preço maior que zero antes de confirmar. Ofertas sem preço: 1003.'
        ):
            confirmar_revisao(self.gestora, sem_preco.pk)
        catalogo = confirmar_revisao(self.gestora, marcadas.pk)

        self.assertEqual(len(catalogo.ofertas()), 8)

    def test_manter_1_e_decisao_explicita_guardada_ao_confirmar_e_a_sugestao_nao_reaparece(self):
        # Decisão da usuária (2026-11-05): manter 1 entra no histórico mesmo sem mudar o valor, exceção à
        # regra do ticket 07. Como o Aceitar, fica na Revisão até a confirmação; abandonar descarta.
        tesoura = CartaoFicticio('3001', 'Tesoura Ficticia C/3')
        revisao = self.importar([tesoura])
        abandonada = self.importar([CartaoFicticio('3005', 'Copo Ficticio C/6')])
        manter_conteudo_1(self.gestora, obter_revisao(self.gestora, revisao.pk).ofertas_propostas()[0].pk)
        manter_conteudo_1(self.gestora, obter_revisao(self.gestora, abandonada.pk).ofertas_propostas()[0].pk)

        self.assertEqual(self.sugestoes(revisao), {'3001': None})
        self.assertEqual(list(historico_do_conteudo(self.gestora, self.fornecedor, '3001')), [])
        informar_condicoes_do_catalogo(self.gestora, revisao.pk, '0')
        confirmar_revisao(self.gestora, revisao.pk, hoje=date(2026, 3, 3))
        abandonar_revisao(self.gestora, abandonada.pk)

        self.assertEqual(
            [(r.gestor.get_username(), r.data, r.valor_anterior, r.valor_novo)
             for r in historico_do_conteudo(self.gestora, self.fornecedor, '3001')],
            [('gestora', date(2026, 3, 3), 1, 1)],
        )
        seguinte = self.importar([tesoura, CartaoFicticio('3005', 'Copo Ficticio C/6')])
        self.assertEqual(self.sugestoes(seguinte), {'3001': None, '3005': 6})

    def contagem(self, revisao):
        revisao = obter_revisao(self.gestora, revisao.pk)
        return revisao.precos_no_arquivo, revisao.ofertas_extraidas, revisao.ofertas_que_faltam

    def sugestoes(self, revisao):
        ofertas = obter_revisao(self.gestora, revisao.pk).ofertas_propostas()
        return {oferta.codigo: oferta.sugestao_de_conteudo for oferta in ofertas}
