"""Testes pelo cliente HTTP: só login obrigatório e ligação com o caso de uso."""

from django.test import TestCase
from django.urls import reverse

from catalogos.casos_de_uso import listar_fornecedores
from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor, nomes


class TelaDeFornecedoresTests(TestCase):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.url = reverse('fornecedores')

    def test_tela_de_fornecedores_so_abre_com_login(self):
        resposta = self.client.get(self.url)

        self.assertRedirects(resposta, f'{reverse("entrar")}?next={self.url}')

    def test_tela_de_fornecedores_cadastra_pelo_caso_de_uso_e_mostra_a_lista(self):
        self.client.login(username='gestora', password=SENHA_DE_TESTE)

        self.client.post(self.url, {'nome': '  Fornecedor Alfa  '})
        repetido = self.client.post(self.url, {'nome': 'fornecedor alfa'})
        lista = self.client.get(self.url)

        self.assertEqual(nomes(listar_fornecedores(self.gestora)), ['Fornecedor Alfa'])
        self.assertContains(repetido, 'Já existe um Fornecedor chamado Fornecedor Alfa.')
        self.assertContains(lista, 'Fornecedor Alfa')
