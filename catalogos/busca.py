"""Texto de busca: sem acentos e em minúsculas, para a busca ignorar maiúsculas e acentos no banco."""

import unicodedata


def normalizar(texto):
    """"Plástica Média" -> "plastica media"."""
    decomposto = unicodedata.normalize('NFKD', texto.casefold())
    return ''.join(c for c in decomposto if not unicodedata.combining(c))


def texto_de_busca(codigo, descricao):
    """O que a Oferta guarda para ser achada: código e descrição normalizados, separados por uma
    quebra de linha, que a gestora não digita (assim um trecho nunca atravessa os dois).
    """
    return normalizar(f'{codigo}\n{descricao}')
