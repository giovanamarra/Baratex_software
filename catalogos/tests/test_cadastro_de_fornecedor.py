from django.test import TestCase

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_fornecedores
from contas.auxiliares_de_teste import criar_gestor


def nomes(fornecedores):
    return [fornecedor.nome for fornecedor in fornecedores]


class CadastroDeFornecedorTests(TestCase):
    def setUp(self):
        self.gestora = criar_gestor('gestora')

    def test_fornecedor_cadastrado_aparece_na_lista_de_fornecedores(self):
        cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

        self.assertEqual(nomes(listar_fornecedores(self.gestora)), ['Fornecedor Alfa'])

    def test_outro_gestor_ve_o_fornecedor_cadastrado_porque_a_base_e_do_grupo(self):
        outro_gestor = criar_gestor('outro-gestor')

        cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')

        self.assertEqual(nomes(listar_fornecedores(outro_gestor)), ['Fornecedor Alfa'])

    def test_nome_do_fornecedor_e_guardado_sem_espacos_nas_pontas(self):
        cadastrar_fornecedor(self.gestora, '  Fornecedor Beta  ')

        self.assertEqual(nomes(listar_fornecedores(self.gestora)), ['Fornecedor Beta'])
