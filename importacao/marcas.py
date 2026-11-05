"""Marcas de conferência da Revisão (ticket 08; ADR-0006). Derivadas, nunca gravadas.

As regras foram calibradas com os Catálogos reais; os números estão no ticket 08.
"""

import statistics

FATOR_FORA_DO_PADRAO = 10
MINIMO_DE_PRECOS_PARA_O_PADRAO = 5


def mediana_dos_precos(precos):
    """Mediana dos preços impressos do Catálogo. Sem preço e preço zero não entram.

    Com menos de 5 preços não há padrão (None): nada fica fora dele.
    """
    validos = [preco for preco in precos if preco]
    return statistics.median(validos) if len(validos) >= MINIMO_DE_PRECOS_PARA_O_PADRAO else None


def fora_do_padrao(preco, mediana):
    """Mais de 10 vezes a mediana do próprio Catálogo, ou menos de um décimo dela."""
    if not preco or mediana is None:
        return False
    return preco > mediana * FATOR_FORA_DO_PADRAO or preco < mediana / FATOR_FORA_DO_PADRAO
