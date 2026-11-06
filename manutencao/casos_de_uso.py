"""Backup e restauração da instalação (ticket 11).

Chamados pelos comandos `fazer_backup` e `restaurar_backup` do manage.py.

O .zip leva o banco (`banco.sqlite3`), a pasta de arquivos inteira, com as subpastas (`arquivos/...`), e
um manifesto (`manifesto.json`) que identifica um backup do sistema.
O banco é copiado pela API de backup do SQLite, nunca copiando o arquivo .sqlite3 direto: assim o backup
funciona com o sistema aberto.
"""

import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.utils import timezone

from catalogos.models import Catalogo
from comparador.erros import ErroDeNegocio

BANCO = 'banco.sqlite3'
ARQUIVOS = 'arquivos/'
MANIFESTO = 'manifesto.json'
FORMATO = 'backup do Comparador de Catálogos'
VERSAO_DO_FORMATO = 1

NAO_E_BACKUP = 'Este arquivo não é um backup do Comparador de Catálogos.'


def fazer_backup(pasta_destino, agora=None):
    """Gera, na pasta de destino, um único .zip com o banco e a pasta de arquivos inteira."""
    pasta_destino = Path(pasta_destino)
    if not pasta_destino.is_dir():
        raise ErroDeNegocio(f'A pasta de destino não existe: {pasta_destino}.')
    agora = agora or timezone.localtime()
    backup = pasta_destino / f'backup-comparador-{agora:%Y-%m-%d_%H-%M-%S}.zip'
    pasta_de_arquivos = Path(settings.MEDIA_ROOT)
    with tempfile.TemporaryDirectory() as temporaria, zipfile.ZipFile(backup, 'w', zipfile.ZIP_DEFLATED) as zip_:
        copia_do_banco = Path(temporaria) / BANCO
        _copiar_banco(_conexao_sqlite(), copia_do_banco)
        zip_.write(copia_do_banco, BANCO)
        zip_.writestr(MANIFESTO, json.dumps({
            'formato': FORMATO,
            'versao': VERSAO_DO_FORMATO,
            'data': agora.isoformat(),
            'catalogos': Catalogo.objects.count(),
        }, ensure_ascii=False, indent=2))
        if pasta_de_arquivos.exists():
            for arquivo in sorted(pasta_de_arquivos.rglob('*')):
                if arquivo.is_file():
                    zip_.write(arquivo, ARQUIVOS + arquivo.relative_to(pasta_de_arquivos).as_posix())
    return backup


def restaurar_backup(arquivo):
    """Traz de volta o banco e a pasta de arquivos de um backup, só numa instalação sem Catálogos."""
    if Catalogo.objects.exists():
        raise ErroDeNegocio(
            'Esta instalação já tem dados. Restaure numa instalação vazia para não perder o que foi feito '
            'depois do backup.'
        )
    pasta_de_arquivos = Path(settings.MEDIA_ROOT)
    with tempfile.TemporaryDirectory() as temporaria, zipfile.ZipFile(arquivo) as zip_:
        _exigir_manifesto(zip_)
        zip_.extract(BANCO, temporaria)
        origem = sqlite3.connect(Path(temporaria) / BANCO)
        try:
            origem.backup(_conexao_sqlite())
        finally:
            origem.close()
        for nome in zip_.namelist():
            if nome.startswith(ARQUIVOS) and not nome.endswith('/'):
                destino = pasta_de_arquivos / nome.removeprefix(ARQUIVOS)
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(zip_.read(nome))


def _exigir_manifesto(zip_):
    try:
        manifesto = json.loads(zip_.read(MANIFESTO))
    except (KeyError, ValueError):
        raise ErroDeNegocio(NAO_E_BACKUP)
    if not isinstance(manifesto, dict) or manifesto.get('formato') != FORMATO:
        raise ErroDeNegocio(NAO_E_BACKUP)


def _conexao_sqlite():
    connection.ensure_connection()
    return connection.connection


def _copiar_banco(conexao, caminho):
    copia = sqlite3.connect(caminho)
    try:
        conexao.backup(copia)
    finally:
        copia.close()
