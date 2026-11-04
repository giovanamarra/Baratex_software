"""Testes pelo cliente HTTP: só login obrigatório e autorização (spec, Testing Decisions)."""

from django.test import TestCase
from django.urls import URLPattern, get_resolver, reverse

from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor, criar_loja

PAGINAS_PUBLICAS = {'entrar'}


def paginas_do_sistema():
    """URLs de todas as páginas do projeto, menos o login e o painel administrativo."""
    for padrao in get_resolver().url_patterns:
        if isinstance(padrao, URLPattern) and padrao.name not in PAGINAS_PUBLICAS:
            argumentos = {nome: 1 for nome in padrao.pattern.converters}
            yield reverse(padrao.name, kwargs=argumentos)


class AcessoSemLoginTests(TestCase):
    def test_sem_login_qualquer_pagina_leva_ao_login(self):
        paginas = list(paginas_do_sistema())
        self.assertIn('/', paginas)

        for pagina in paginas:
            with self.subTest(pagina=pagina):
                resposta = self.client.get(pagina)
                self.assertRedirects(resposta, f'{reverse("entrar")}?next={pagina}')


class EntrarTests(TestCase):
    def test_senha_errada_mostra_usuario_ou_senha_incorretos(self):
        criar_gestor('gestora')

        resposta = self.client.post(
            reverse('entrar'), {'username': 'gestora', 'password': 'senha-errada'}
        )

        self.assertContains(resposta, 'Usuário ou senha incorretos.')
        self.assertNotIn('_auth_user_id', self.client.session)


class TelasDoGestorTests(TestCase):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.outro_gestor = criar_gestor('outro-gestor')
        criar_loja(self.gestora, 'Loja Centro')
        criar_loja(self.gestora, 'Loja Norte')
        self.loja_sul = criar_loja(self.outro_gestor, 'Loja Sul')
        self.client.login(username='gestora', password=SENHA_DE_TESTE)

    def test_pagina_inicial_mostra_as_lojas_do_gestor_e_nao_as_de_outro(self):
        resposta = self.client.get(reverse('inicio'))

        self.assertContains(resposta, 'Loja Centro')
        self.assertContains(resposta, 'Loja Norte')
        self.assertNotContains(resposta, 'Loja Sul')
