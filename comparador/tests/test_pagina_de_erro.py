"""Com DEBUG desligado, um erro inesperado mostra uma página simples em português (ticket 11)."""

from django.contrib.auth.decorators import login_not_required
from django.test import TestCase, override_settings
from django.urls import path

from comparador.urls import urlpatterns as urls_da_aplicacao


@login_not_required
def tela_que_estoura(request):
    raise RuntimeError('defeito de teste')


urlpatterns = [path('estoura/', tela_que_estoura), *urls_da_aplicacao]


@override_settings(ROOT_URLCONF=__name__, DEBUG=False)
class PaginaDeErroTests(TestCase):
    def test_erro_inesperado_mostra_pagina_em_portugues_sem_o_detalhe_tecnico(self):
        self.client.raise_request_exception = False

        with self.assertLogs('django.request', 'ERROR'):  # o detalhe vai para o terminal, não para a tela
            resposta = self.client.get('/estoura/')

        self.assertEqual(resposta.status_code, 500)
        self.assertContains(resposta, 'Algo deu errado', status_code=500)
        self.assertContains(resposta, 'logo-baratex-contorno.png', status_code=500)
        self.assertNotContains(resposta, 'defeito de teste', status_code=500)
