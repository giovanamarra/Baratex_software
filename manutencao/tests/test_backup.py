"""Backup e restauração da instalação no computador da gestora (ticket 11)."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from importacao.auxiliares_de_teste import TesteTransacionalComArquivosEnviados
from manutencao.casos_de_uso import fazer_backup


class BackupTests(TesteTransacionalComArquivosEnviados):
    # Transacional: a API de backup do SQLite não copia para dentro de uma transação aberta.

    def setUp(self):
        self.destino = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.destino, ignore_errors=True)

    def test_backup_gera_um_unico_arquivo_com_a_data_e_a_hora_no_nome(self):
        backup = fazer_backup(self.destino, agora=datetime(2026, 11, 5, 14, 30, 7))

        self.assertEqual(list(self.destino.iterdir()), [backup])
        self.assertEqual(backup.name, 'backup-comparador-2026-11-05_14-30-07.zip')
