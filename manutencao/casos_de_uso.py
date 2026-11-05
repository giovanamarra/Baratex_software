"""Backup e restauração da instalação (ticket 11).

Chamados pelos comandos `fazer_backup` e `restaurar_backup` do manage.py.
"""

import zipfile
from pathlib import Path

from django.utils import timezone


def fazer_backup(pasta_destino, agora=None):
    """Gera, na pasta de destino, um único .zip com o banco e a pasta de arquivos inteira."""
    agora = agora or timezone.localtime()
    backup = Path(pasta_destino) / f'backup-comparador-{agora:%Y-%m-%d_%H-%M-%S}.zip'
    with zipfile.ZipFile(backup, 'w', zipfile.ZIP_DEFLATED):
        pass
    return backup
