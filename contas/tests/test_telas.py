"""Testes pelo cliente HTTP: só login obrigatório e autorização (spec, Testing Decisions)."""

from django.test import TestCase
from django.urls import URLPattern, get_resolver, reverse

from contas.auxiliares_de_teste import criar_gestor

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
