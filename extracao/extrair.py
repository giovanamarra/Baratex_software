"""Interface do módulo Extração: arquivo enviado -> Ofertas propostas. Não grava nada."""

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException

from comparador.erros import ErroDeNegocio
from extracao.grade_de_cartoes import e_layout_a, ler_layout_a

# PROVISÓRIO: só existe o caminho de grade de cartões. Os tickets 23 (tabela em PDF) e 25 (LLM)
# trocam esta recusa por outro caminho de extração.
MENSAGEM_PROVISORIA_LAYOUT_DESCONHECIDO = (
    'Não reconheci o Layout deste PDF. Por enquanto, só Catálogos em grade de cartões '
    'de Layouts conhecidos podem ser importados.'
)


# PROVISÓRIO: os tickets 21 (Excel) e 25 (imagem, pela LLM) acrescentam os outros formatos.
MENSAGEM_PROVISORIA_FORMATO = 'Por enquanto, só Catálogos em PDF de grade de cartões podem ser importados.'
ASSINATURA_DE_PDF = b'%PDF'


def extrair_ofertas(arquivo):
    # O formato vem do conteúdo, não da extensão: um Excel renomeado para .pdf continua sendo Excel.
    inicio = arquivo.read(len(ASSINATURA_DE_PDF))
    arquivo.seek(0)
    if inicio != ASSINATURA_DE_PDF:
        raise ErroDeNegocio(MENSAGEM_PROVISORIA_FORMATO)
    try:
        with pdfplumber.open(arquivo) as pdf:
            if not e_layout_a(pdf):
                raise ErroDeNegocio(MENSAGEM_PROVISORIA_LAYOUT_DESCONHECIDO)
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
