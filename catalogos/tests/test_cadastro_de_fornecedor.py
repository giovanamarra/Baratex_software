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
