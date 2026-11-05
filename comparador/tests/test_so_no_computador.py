"""A aplicação atende só o próprio computador da gestora (ticket 11)."""

from django.test import TestCase
from django.urls import reverse


class SoNoProprioComputadorTests(TestCase):
    def test_atende_pelo_endereco_do_proprio_computador(self):
        for endereco in ['127.0.0.1:8000', 'localhost:8000']:
            with self.subTest(endereco=endereco):
                resposta = self.client.get(reverse('entrar'), HTTP_HOST=endereco)

                self.assertEqual(resposta.status_code, 200)

    def test_recusa_pedido_vindo_pelo_endereco_de_outra_maquina_da_rede(self):
        resposta = self.client.get(reverse('entrar'), HTTP_HOST='192.168.0.10:8000')

        self.assertEqual(resposta.status_code, 400)
