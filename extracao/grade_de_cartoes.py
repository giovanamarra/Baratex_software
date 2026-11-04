"""Caminho 1 da extração: grade de cartões, com um leitor determinístico por Layout (ADR-0006)."""

from dataclasses import dataclass
from decimal import Decimal

CAMINHO = 'grade de cartões'


@dataclass(frozen=True)
class OfertaExtraida:
    codigo: str
    descricao: str
    preco_impresso: Decimal | None
    caixa: int | None
    caminho: str


# Layout A: cada cartão tem "Código:<código> Cx: <n>", com o preço "R$" acima e a descrição logo abaixo.
ROTULO_CODIGO = 'Código:'
ROTULO_CAIXA = 'Cx:'
LARGURA_DO_CARTAO = 135
TOLERANCIA_DE_LINHA = 3
DISTANCIA_DA_DESCRICAO = 12  # a descrição fica ~12 pt abaixo da linha do código
ALTURA_ACIMA_DO_CODIGO = 40  # o preço fica até ~26 pt acima da linha do código


def ler_layout_a(pdf):
    ofertas = []
    for pagina in pdf.pages:
        palavras = pagina.extract_words()
        ancoras = [p for p in palavras if p['text'].startswith(ROTULO_CODIGO)]
        # Ordem de leitura: linha da grade, depois coluna.
        for ancora in sorted(ancoras, key=lambda p: (round(p['top'] / 20), p['x0'])):
            ofertas.append(_ler_cartao(ancora, palavras))
    return ofertas


def _ler_cartao(ancora, palavras):
    x, topo = ancora['x0'], ancora['top']
    celula = [
        p for p in palavras
        if x - 2 <= p['x0'] < x + LARGURA_DO_CARTAO and topo - ALTURA_ACIMA_DO_CODIGO <= p['top'] <= topo + 20
    ]

    def linha(deslocamento):
        alvo = topo + deslocamento
        return sorted((p for p in celula if abs(p['top'] - alvo) <= TOLERANCIA_DE_LINHA), key=lambda p: p['x0'])

    precos = [p['text'] for p in celula if p['text'].startswith('R$') and p['top'] < topo]
    return OfertaExtraida(
        codigo=ancora['text'][len(ROTULO_CODIGO):],
        descricao=' '.join(p['text'] for p in linha(DISTANCIA_DA_DESCRICAO)),
        preco_impresso=_preco(precos[0]) if precos else None,
        caixa=_caixa([p['text'] for p in linha(0)]),
        caminho=CAMINHO,
    )


def _preco(texto):
    # "R$1.234,56" -> Decimal("1234.56")
    return Decimal(texto[2:].replace('.', '').replace(',', '.'))


def _caixa(textos_da_linha_do_codigo):
    for posicao, texto in enumerate(textos_da_linha_do_codigo):
        if texto.startswith(ROTULO_CAIXA):
            valor = texto[len(ROTULO_CAIXA):] or next(iter(textos_da_linha_do_codigo[posicao + 1:]), '')
            return int(valor) if valor.isdigit() else None
    return None
