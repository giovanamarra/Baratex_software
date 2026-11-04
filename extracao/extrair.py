"""Interface do módulo Extração: arquivo enviado -> Ofertas propostas. Não grava nada."""

import pdfplumber

from extracao.grade_de_cartoes import ler_layout_a


def extrair_ofertas(arquivo):
    with pdfplumber.open(arquivo) as pdf:
        return ler_layout_a(pdf)
