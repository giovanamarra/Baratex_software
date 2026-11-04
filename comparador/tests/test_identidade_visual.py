"""A identidade visual segue docs/design/BRAND.md."""

import re

from django.conf import settings
from django.test import SimpleTestCase

RAIZ = settings.BASE_DIR
TOKENS = RAIZ / 'static' / 'css' / 'tokens.css'


def bloco_css_do_brand():
    brand = (RAIZ / 'docs' / 'design' / 'BRAND.md').read_text(encoding='utf-8')
    return re.search(r'```css\n(.*?)```', brand, re.DOTALL).group(1)


class IdentidadeVisualTests(SimpleTestCase):
    def test_tokens_css_e_exatamente_o_bloco_de_tokens_do_brand(self):
        self.assertTrue(TOKENS.exists(), f'{TOKENS} não existe')
        self.assertEqual(TOKENS.read_text(encoding='utf-8').strip(), bloco_css_do_brand().strip())
