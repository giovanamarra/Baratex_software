"""A identidade visual segue docs/design/BRAND.md."""

import re

from django.conf import settings
from django.test import SimpleTestCase

RAIZ = settings.BASE_DIR
TOKENS = RAIZ / 'static' / 'css' / 'tokens.css'
# Cor em hex: #abc, #abcd, #aabbcc ou #aabbccdd. Ignora entidades HTML como &#123;.
COR_HEX = re.compile(r'(?<![&\w])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b')


def bloco_css_do_brand():
    brand = (RAIZ / 'docs' / 'design' / 'BRAND.md').read_text(encoding='utf-8')
    return re.search(r'```css\n(.*?)```', brand, re.DOTALL).group(1)


class IdentidadeVisualTests(SimpleTestCase):
    def test_tokens_css_e_exatamente_o_bloco_de_tokens_do_brand(self):
        self.assertTrue(TOKENS.exists(), f'{TOKENS} não existe')
        self.assertEqual(TOKENS.read_text(encoding='utf-8').strip(), bloco_css_do_brand().strip())

    def test_nenhuma_cor_em_hex_fora_de_tokens_css(self):
        arquivos = [
            *(RAIZ / 'templates').rglob('*.html'),
            *(caminho for caminho in (RAIZ / 'static' / 'css').rglob('*.css') if caminho != TOKENS),
        ]
        self.assertIn(RAIZ / 'templates' / 'base.html', arquivos)
        self.assertIn(RAIZ / 'static' / 'css' / 'base.css', arquivos)

        achados = [
            f'{caminho.relative_to(RAIZ)}:{numero}: {cor}'
            for caminho in arquivos
            for numero, linha in enumerate(caminho.read_text(encoding='utf-8').splitlines(), 1)
            for cor in COR_HEX.findall(linha)
        ]
        self.assertEqual(achados, [], 'Use as variáveis de tokens.css em vez de hex.')
