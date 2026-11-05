"""Segredos e pastas vêm do arquivo .env, fora do git (ticket 11)."""

import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from comparador.ambiente import ler_configuracao


class LerConfiguracaoTests(SimpleTestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.pasta, ignore_errors=True)
        self.env = self.pasta / '.env'

    def test_sem_env_inicia_com_valores_de_desenvolvimento_sem_debug_e_sem_chave_e_avisa(self):
        configuracao = ler_configuracao(self.env)

        self.assertFalse(configuracao.debug)
        self.assertEqual(configuracao.chave_da_llm, '')
        self.assertTrue(configuracao.secret_key)
        self.assertEqual(configuracao.pasta_de_arquivos, Path.home() / 'ComparadorDeCatalogos' / 'arquivos')
        self.assertFalse(configuracao.pasta_de_arquivos.is_relative_to(settings.BASE_DIR))
        self.assertIn(str(self.env), configuracao.aviso)
        self.assertIn('.env.exemplo', configuracao.aviso)
