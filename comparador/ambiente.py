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
    if caminho_do_env.exists():
        valores, aviso = _ler_env(caminho_do_env), ''
    else:
        valores = {}
        aviso = (
            f'Aviso: o arquivo {caminho_do_env} não existe. O sistema vai usar valores de desenvolvimento. '
            'Para a instalação de uso, copie .env.exemplo para .env e preencha.'
        )
    pasta = valores.get('PASTA_DE_ARQUIVOS')
    return Configuracao(
        secret_key=valores.get('SECRET_KEY') or SECRET_KEY_DE_DESENVOLVIMENTO,
        debug=valores.get('DEBUG', '').lower() in ('true', 'sim', '1'),
        chave_da_llm=valores.get('ANTHROPIC_API_KEY', ''),
        pasta_de_arquivos=Path(pasta).expanduser() if pasta else _pasta_de_arquivos_padrao(),
        aviso=aviso,
    )


def _ler_env(caminho):
    valores = {}
    for linha in caminho.read_text(encoding='utf-8').splitlines():
        linha = linha.strip()
        if not linha or linha.startswith('#') or '=' not in linha:
            continue
        nome, valor = linha.split('=', 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in '"\'':
            valor = valor[1:-1]
        valores[nome.strip()] = valor
    return valores


def _pasta_de_arquivos_padrao():
    return Path.home() / 'ComparadorDeCatalogos' / 'arquivos'
