"""Configuração da instalação: segredos e pastas lidos do arquivo .env, que fica fora do git (ticket 11).

Lido sem biblioteca: uma linha por valor, no formato NOME=valor.
"""

from dataclasses import dataclass
from pathlib import Path

# Só para desenvolvimento: a instalação da gestora tem a própria SECRET_KEY no .env.
SECRET_KEY_DE_DESENVOLVIMENTO = 'django-insecure-84a7()ka28^i#pm_iuq7(ceib#&)yd*@1$1a*ilfwmu^ob)*pn'


@dataclass
class Configuracao:
    secret_key: str
    debug: bool
    chave_da_llm: str
    pasta_de_arquivos: Path
    aviso: str = ''  # vazio quando o .env foi encontrado


def ler_configuracao(caminho_do_env):
    caminho_do_env = Path(caminho_do_env)
    return Configuracao(
        secret_key=SECRET_KEY_DE_DESENVOLVIMENTO,
        debug=False,
        chave_da_llm='',
        pasta_de_arquivos=_pasta_de_arquivos_padrao(),
        aviso=(
            f'Aviso: o arquivo {caminho_do_env} não existe. O sistema vai usar valores de desenvolvimento. '
            'Para a instalação de uso, copie .env.exemplo para .env e preencha.'
        ),
    )


def _pasta_de_arquivos_padrao():
    return Path.home() / 'ComparadorDeCatalogos' / 'arquivos'
