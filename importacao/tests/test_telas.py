"""Testes pelo cliente HTTP: só login obrigatório e autorização (spec, Testing Decisions)."""

from decimal import Decimal

from django.urls import reverse

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_catalogos_do_fornecedor
from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import iniciar_importacao, listar_revisoes_em_andamento, obter_revisao


class TelasDeImportacaoTests(TesteComArquivosEnviados):
    def test_abrir_pela_url_a_revisao_de_outro_gestor_e_recusado(self):
        gestora = criar_gestor('gestora')
        criar_gestor('outro-gestor')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio')]))
        revisao = iniciar_importacao(gestora, fornecedor, catalogo)
        self.client.login(username='outro-gestor', password=SENHA_DE_TESTE)

        resposta = self.client.get(reverse('revisao', kwargs={'pk': revisao.pk}))

        self.assertContains(resposta, 'Esta Revisão é de outro Gestor.', status_code=403)
        self.assertNotContains(resposta, 'Balde Ficticio', status_code=403)

    def test_outro_gestor_nao_confirma_nem_abandona_a_revisao_pela_url(self):
        gestora = criar_gestor('gestora')
        criar_gestor('outro-gestor')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio')]))
        revisao = iniciar_importacao(gestora, fornecedor, catalogo)
        self.client.login(username='outro-gestor', password=SENHA_DE_TESTE)
        confirmar = reverse('confirmar_revisao', kwargs={'pk': revisao.pk})
        abandonar = reverse('abandonar_revisao', kwargs={'pk': revisao.pk})
        tentativas = {
            'confirmar': lambda: self.client.post(confirmar),
            'abrir a confirmação do abandono': lambda: self.client.get(abandonar),
            'abandonar': lambda: self.client.post(abandonar),
        }

        for tentativa, requisicao in tentativas.items():
            with self.subTest(tentativa=tentativa):
                self.assertContains(requisicao(), 'Esta Revisão é de outro Gestor.', status_code=403)

        self.assertEqual([r.pk for r in listar_revisoes_em_andamento(gestora)], [revisao.pk])
        self.assertEqual(list(listar_catalogos_do_fornecedor(gestora, fornecedor)), [])

    def test_outro_gestor_nao_informa_desconto_na_revisao_pela_url(self):
        gestora = criar_gestor('gestora')
        criar_gestor('outro-gestor')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio', '10,00')]))
        revisao = iniciar_importacao(gestora, fornecedor, catalogo)
        self.client.login(username='outro-gestor', password=SENHA_DE_TESTE)

        resposta = self.client.post(
            reverse('informar_condicoes_do_catalogo', kwargs={'pk': revisao.pk}), {'desconto': '50'}
        )

        self.assertContains(resposta, 'Esta Revisão é de outro Gestor.', status_code=403)
        ofertas = obter_revisao(gestora, revisao.pk).ofertas_propostas()
        self.assertEqual([oferta.preco_unitario for oferta in ofertas], [Decimal('10.00')])

    def test_outro_gestor_nao_corrige_adiciona_nem_remove_ofertas_da_revisao_pela_url(self):
        gestora = criar_gestor('gestora')
        criar_gestor('outro-gestor')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        catalogo = arquivo_enviado(catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio', '10,00')]))
        revisao = iniciar_importacao(gestora, fornecedor, catalogo)
        balde = revisao.ofertas_propostas()[0]
        self.client.login(username='outro-gestor', password=SENHA_DE_TESTE)
        corrigir = reverse('corrigir_oferta_proposta', kwargs={'pk': balde.pk})
        adicionar = reverse('adicionar_oferta_proposta', kwargs={'pk': revisao.pk})
        remover = reverse('remover_oferta_proposta', kwargs={'pk': balde.pk})
        valores = {'codigo': '9999', 'descricao': 'Invasora', 'preco_impresso': '1,00', 'caixa': '1'}
        tentativas = {
            'abrir Corrigir': lambda: self.client.get(corrigir),
            'corrigir': lambda: self.client.post(corrigir, valores),
            'abrir Adicionar': lambda: self.client.get(adicionar),
            'adicionar': lambda: self.client.post(adicionar, valores),
            'abrir a confirmação de Remover': lambda: self.client.get(remover),
            'remover': lambda: self.client.post(remover),
        }

        for tentativa, requisicao in tentativas.items():
            with self.subTest(tentativa=tentativa):
                self.assertContains(requisicao(), 'Esta Revisão é de outro Gestor.', status_code=403)

        ofertas = obter_revisao(gestora, revisao.pk).ofertas_propostas()
        self.assertEqual([(oferta.codigo, oferta.preco_impresso) for oferta in ofertas], [('1001', Decimal('10.00'))])
