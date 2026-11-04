"""Interface do módulo Extração: arquivo enviado -> Ofertas propostas. Não grava nada."""

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException

from comparador.erros import ErroDeNegocio
from extracao.grade_de_cartoes import ler_layout_a


def extrair_ofertas(arquivo):
    try:
        with pdfplumber.open(arquivo) as pdf:
            ofertas = ler_layout_a(pdf)
    except PdfminerException:
        raise ErroDeNegocio(
            'Não consegui abrir este arquivo. Ele pode estar corrompido: peça ao Fornecedor que envie de novo.'
        )
    if not any(oferta.preco_impresso is not None for oferta in ofertas):
        raise ErroDeNegocio(
            'Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.'
        )
    return ofertas
