from django.test import TestCase

from contas.auxiliares_de_teste import criar_gestor, criar_loja, nomes
from contas.casos_de_uso import listar_minhas_lojas


class LojasDoGestorTests(TestCase):
    def setUp(self):
        self.gestora = criar_gestor('gestora')
        self.outro_gestor = criar_gestor('outro-gestor')
        self.loja_centro = criar_loja(self.gestora, 'Loja Centro')
        criar_loja(self.gestora, 'Loja Norte')
        self.loja_sul = criar_loja(self.outro_gestor, 'Loja Sul')
        criar_loja(self.outro_gestor, 'Loja Leste')

    def test_listar_as_minhas_lojas_devolve_so_as_lojas_do_gestor(self):
        self.assertCountEqual(
            nomes(listar_minhas_lojas(self.gestora)), ['Loja Centro', 'Loja Norte']
        )
