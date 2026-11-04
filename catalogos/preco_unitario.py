"""Preço unitário (ADR-0005). Sempre derivado, nunca gravado; só Decimal, nunca float."""

from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal('0.01')


def calcular_preco_unitario(preco_impresso, conteudo):
    if preco_impresso is None:
        return None
    return (preco_impresso / conteudo).quantize(CENTAVO, rounding=ROUND_HALF_UP)
