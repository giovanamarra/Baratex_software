"""Testes pelo cliente HTTP: só login obrigatório e autorização (spec, Testing Decisions)."""

from django.test import TestCase
from django.urls import URLPattern, get_resolver, reverse

from contas.auxiliares_de_teste import SENHA_DE_TESTE, criar_gestor, criar_loja, nomes
from contas.casos_de_uso import listar_minhas_lojas

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

    def test_editar_pela_url_a_loja_de_outro_gestor_e_recusado_e_a_loja_nao_muda(self):
        url = reverse('editar_loja', kwargs={'pk': self.loja_sul.pk})
        tentativas = {
            'abrir o formulário': lambda: self.client.get(url),
            'enviar o formulário': lambda: self.client.post(url, {'nome': 'Loja Invadida'}),
        }

        for tentativa, requisicao in tentativas.items():
            with self.subTest(tentativa=tentativa):
                resposta = requisicao()
                self.assertContains(
                    resposta, 'Esta Loja é de outro Gestor. Só ele pode editá-la.', status_code=403
                )

        self.assertEqual(nomes(listar_minhas_lojas(self.outro_gestor)), ['Loja Sul'])

    def test_depois_de_sair_a_proxima_pagina_pede_login(self):
        self.client.post(reverse('sair'))

        resposta = self.client.get(reverse('inicio'))

        self.assertRedirects(resposta, f'{reverse("entrar")}?next={reverse("inicio")}')
