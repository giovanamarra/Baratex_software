"""Auxiliares dos testes de Importação, reutilizados pelos próximos tickets."""

import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings


class TesteComArquivosEnviados(TestCase):
    """Guarda os arquivos enviados numa pasta temporária, apagada no fim. Nunca em media/."""

    @classmethod
    def setUpClass(cls):
        cls._pasta_de_arquivos = tempfile.mkdtemp()
        cls._media_temporaria = override_settings(MEDIA_ROOT=cls._pasta_de_arquivos)
        cls._media_temporaria.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_temporaria.disable()
        shutil.rmtree(cls._pasta_de_arquivos, ignore_errors=True)


def arquivo_enviado(conteudo, nome='catalogo.pdf'):
    return SimpleUploadedFile(nome, conteudo)


def resumo(oferta):
    """Os campos que a Revisão e o Catálogo guardam de uma Oferta, para comparar em testes."""
    return (oferta.codigo, oferta.descricao, oferta.preco_impresso, oferta.caixa, oferta.caminho)
