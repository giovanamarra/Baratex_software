"""Os comandos do manage.py que a gestora roda para fazer backup e restaurar (ticket 11)."""

import shutil
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import CommandError, call_command

from contas.auxiliares_de_teste import criar_gestor
from contas.models import Gestor
from importacao.auxiliares_de_teste import TesteTransacionalComArquivosEnviados
from manutencao.casos_de_uso import fazer_backup


class ComandosDeBackupTests(TesteTransacionalComArquivosEnviados):
    def setUp(self):
        self.destino = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.destino, ignore_errors=True)

    def test_fazer_backup_grava_o_arquivo_na_pasta_e_diz_onde_ficou(self):
        saida = StringIO()

        call_command('fazer_backup', str(self.destino), stdout=saida)

        [backup] = self.destino.iterdir()
        self.assertIn(f'Pronto: backup gravado em {backup}', saida.getvalue())

    def test_fazer_backup_para_pasta_inexistente_mostra_a_mensagem_sem_detalhe_tecnico(self):
        inexistente = self.destino / 'pendrive-desconectado'

        with self.assertRaisesMessage(CommandError, f'A pasta de destino não existe: {inexistente}.'):
            call_command('fazer_backup', str(inexistente))

    def test_restaurar_backup_traz_os_dados_de_volta_e_avisa(self):
        criar_gestor('gestora')
        backup = fazer_backup(self.destino)
        call_command('flush', interactive=False, verbosity=0)
        saida = StringIO()

        call_command('restaurar_backup', str(backup), stdout=saida)

        self.assertTrue(Gestor.objects.filter(username='gestora').exists())
        self.assertIn(f'Pronto: backup {backup.name} restaurado.', saida.getvalue())
