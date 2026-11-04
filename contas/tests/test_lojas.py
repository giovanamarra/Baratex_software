from django.test import TestCase

from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor, criar_loja, nomes
from contas.casos_de_uso import listar_minhas_lojas, renomear_loja


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

    def test_dono_renomeia_a_propria_loja(self):
        renomear_loja(self.gestora, self.loja_centro, 'Loja Praça')

        self.assertCountEqual(
            nomes(listar_minhas_lojas(self.gestora)), ['Loja Praça', 'Loja Norte']
        )

    def test_renomear_loja_de_outro_gestor_e_recusado_e_a_loja_nao_muda(self):
        with self.assertRaisesMessage(
            ErroDeNegocio, 'Esta Loja é de outro Gestor. Só ele pode editá-la.'
        ):
            renomear_loja(self.gestora, self.loja_sul, 'Loja Invadida')

        self.assertCountEqual(
            nomes(listar_minhas_lojas(self.outro_gestor)), ['Loja Sul', 'Loja Leste']
        )
