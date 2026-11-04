"""Formatos de exibição em português."""

from django import template

register = template.Library()


@register.filter
def percentual(desconto):
    """Desconto das Condições do Catálogo para ler: 3 -> "3%", 2.5 -> "2,5%", vazio -> "sem desconto"."""
    if desconto is None:
        return 'sem desconto'
    return f'{percentual_no_campo(desconto)}%'


@register.filter
def percentual_no_campo(desconto):
    """O mesmo número, sem o símbolo, para preencher o campo: 2.5000 -> "2,5"; vazio -> ""."""
    if desconto is None:
        return ''
    return format(desconto.normalize(), 'f').replace('.', ',')
