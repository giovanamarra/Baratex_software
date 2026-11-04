"""Catálogos fictícios para os testes: imitam a estrutura dos reais, sem copiar dados (ADR-0006).

Uso: uma lista de cartões inventados entra, os bytes de um PDF saem.
"""

from dataclasses import dataclass

from fpdf import FPDF

# Geometria medida no Layout A real: A4 em pontos, grade de 4 colunas x 5 linhas, cartões de 140 pt.
COLUNAS = 4
LINHAS = 5
CARTOES_POR_PAGINA = COLUNAS * LINHAS
ORIGEM_X = 18
ORIGEM_Y = 98
LADO_DO_CARTAO = 140
LIMITE_DA_DESCRICAO = 30  # o gerador real corta a descrição em 30 caracteres


@dataclass
class CartaoFicticio:
    """Um cartão do Layout A, com os textos como aparecem impressos."""

    codigo: str
    descricao: str
    preco: str | None = '12,90'  # sem "R$"; None = cartão sem preço
    caixa: str = '24'  # "***" = Caixa mascarada, como em alguns cartões reais
    ipi: str = '+13,0% ipi'  # ou "sem ipi"


def catalogo_ficticio_layout_a(cartoes, rodape='Catálogo de Produtos Fornecedor Fictício'):
    """PDF com texto selecionável, no Layout A, com um cartão por item de `cartoes`."""
    pdf = FPDF(unit='pt', format='A4')
    pdf.set_auto_page_break(False)
    for inicio in range(0, max(len(cartoes), 1), CARTOES_POR_PAGINA):
        pdf.add_page()
        _cabecalho_e_rodape(pdf, rodape)
        for posicao, cartao in enumerate(cartoes[inicio:inicio + CARTOES_POR_PAGINA]):
            linha, coluna = divmod(posicao, COLUNAS)
            _cartao(pdf, cartao, ORIGEM_X + coluna * LADO_DO_CARTAO, ORIGEM_Y + linha * LADO_DO_CARTAO)
    return bytes(pdf.output())


def pdf_ficticio_com_texto(linhas):
    """PDF com texto selecionável, uma linha por item, sem a estrutura de nenhum Layout conhecido."""
    pdf = FPDF(unit='pt', format='A4')
    pdf.add_page()
    for numero, linha in enumerate(linhas):
        _texto(pdf, 40, 60 + numero * 14, 10, linha)
    return bytes(pdf.output())


def _cabecalho_e_rodape(pdf, rodape):
    _texto(pdf, 523, 18, 7.8, f'Página {pdf.page_no()}')
    _texto(pdf, 13, 788, 7.8, rodape)
    _texto(pdf, 13, 798, 7.8, 'Gerado em:01/01/26-10:00:00 Válido até: 31/01/26')
    _texto(pdf, 13, 808, 7.8, '* Os preços podem mudar sem aviso prévio.')


def _cartao(pdf, cartao, x, y):
    # Posições relativas ao canto do cartão, medidas no Layout A real (topo do texto ~ linha de base - 6 pt).
    if cartao.preco is not None:
        _texto(pdf, x + 90, y + 59, 9.4, f'R${cartao.preco}', negrito=True)
        _texto(pdf, x + 90, y + 70, 7.2, cartao.ipi)
    _texto(pdf, x, y + 84, 7.8, f'Código:{cartao.codigo}')
    _texto(pdf, x + 65, y + 85, 7.2, 'Cx:')
    _texto(pdf, x + 80, y + 84, 9.4, cartao.caixa, negrito=True)
    _texto(pdf, x, y + 95, 7.2, cartao.descricao[:LIMITE_DA_DESCRICAO])
    _texto(pdf, x, y + 104, 7.2, f'Ean13:{cartao.codigo.zfill(13)}')
    _texto(pdf, x, y + 113, 7.2, 'Disponibilidade: IMEDIATA')
    _texto(pdf, x + 90, y + 113, 7.2, 'Tag: X-XX')


def _texto(pdf, x, y, tamanho, texto, negrito=False):
    pdf.set_font('Helvetica', 'B' if negrito else '', tamanho)
    pdf.text(x, y, texto)
