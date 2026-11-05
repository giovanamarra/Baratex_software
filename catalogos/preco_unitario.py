"""Preço unitário (ADR-0005). Sempre derivado, nunca gravado; só Decimal, nunca float.

Preço unitário = preço impresso × (1 − desconto%) ÷ Conteúdo, arredondado para centavos
(meio centavo para cima).
"""

from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal('0.01')
CEM = Decimal(100)


def calcular_preco_unitario(preco_impresso, desconto, conteudo):
    """`desconto` é o percentual das Condições do Catálogo (Decimal) ou None, sem desconto."""
    if preco_impresso is None:
        return None
    fator = 1 - (desconto or 0) / CEM
    return (preco_impresso * fator / conteudo).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def acima_do_teto(preco_unitario, teto):
    """Só o Preço unitário acima do Teto é destacado; igual ao Teto não. Sem Teto ou sem preço, nada é destacado."""
    return teto is not None and preco_unitario is not None and preco_unitario > teto
