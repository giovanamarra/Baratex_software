from django.test import TestCase

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_fornecedores
from comparador.erros import ErroDeNegocio
from contas.auxiliares_de_teste import criar_gestor, nomes


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

    def test_fornecedor_sem_nome_e_recusado(self):
        for nome_vazio in ['', '   ']:
            with self.subTest(nome=nome_vazio):
                with self.assertRaisesMessage(ErroDeNegocio, 'Informe o nome do Fornecedor.'):
                    cadastrar_fornecedor(self.gestora, nome_vazio)

        self.assertEqual(nomes(listar_fornecedores(self.gestora)), [])

    def test_fornecedor_com_nome_repetido_e_recusado(self):
        cadastrar_fornecedor(self.gestora, 'Fornecedor Alfa')
        cadastrar_fornecedor(self.gestora, 'Ótica Beta')

        casos = [
            ('Fornecedor Alfa', 'Já existe um Fornecedor chamado Fornecedor Alfa.'),
            ('  fornecedor ALFA  ', 'Já existe um Fornecedor chamado Fornecedor Alfa.'),
            ('ÓTICA BETA', 'Já existe um Fornecedor chamado Ótica Beta.'),
        ]
        for nome_repetido, mensagem in casos:
            with self.subTest(nome=nome_repetido):
                with self.assertRaisesMessage(ErroDeNegocio, mensagem):
                    cadastrar_fornecedor(self.gestora, nome_repetido)

        self.assertCountEqual(
            nomes(listar_fornecedores(self.gestora)), ['Fornecedor Alfa', 'Ótica Beta']
        )
