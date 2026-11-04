"""Interface do módulo Extração: arquivo enviado -> Ofertas propostas. Não grava nada."""

import pdfplumber

from comparador.erros import ErroDeNegocio
from extracao.grade_de_cartoes import ler_layout_a


def extrair_ofertas(arquivo):
    with pdfplumber.open(arquivo) as pdf:
        ofertas = ler_layout_a(pdf)
    if not any(oferta.preco_impresso is not None for oferta in ofertas):
        raise ErroDeNegocio(
            'Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.'
        )
    return ofertas
