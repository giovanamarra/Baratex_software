"""Backup e restauração da instalação no computador da gestora (ticket 11)."""

import shutil
import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management import call_command

from catalogos.casos_de_uso import buscar_ofertas, cadastrar_fornecedor
from contas.auxiliares_de_teste import criar_gestor
from contas.models import Gestor
from extracao.catalogos_ficticios import CartaoFicticio, catalogo_ficticio_layout_a
from importacao.auxiliares_de_teste import TesteTransacionalComArquivosEnviados, arquivo_enviado
from importacao.casos_de_uso import confirmar_revisao, iniciar_importacao, informar_condicoes_do_catalogo
from manutencao.casos_de_uso import fazer_backup, restaurar_backup


class BackupTests(TesteTransacionalComArquivosEnviados):
    # Transacional: a API de backup do SQLite não copia para dentro de uma transação aberta.

    def setUp(self):
        self.destino = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.destino, ignore_errors=True)
        self.pasta_de_arquivos = Path(settings.MEDIA_ROOT)

    def importar_catalogo(self):
        """Importa e confirma um Catálogo fictício do Layout A; devolve o conteúdo do arquivo de origem."""
        gestora = criar_gestor('gestora')
        fornecedor = cadastrar_fornecedor(gestora, 'Fornecedor Alfa')
        conteudo = catalogo_ficticio_layout_a([CartaoFicticio('1001', 'Balde Ficticio', '9,90', '6')])
        revisao = iniciar_importacao(gestora, fornecedor, arquivo_enviado(conteudo), hoje=date(2026, 3, 2))
        informar_condicoes_do_catalogo(gestora, revisao.pk, '0')
        confirmar_revisao(gestora, revisao.pk)
        return conteudo

    def apagar_a_instalacao(self):
        """Como uma instalação nova: banco sem dados e pasta de arquivos vazia."""
        call_command('flush', interactive=False, verbosity=0)
        for item in self.pasta_de_arquivos.iterdir():
            shutil.rmtree(item) if item.is_dir() else item.unlink()

    def test_backup_gera_um_unico_arquivo_com_a_data_e_a_hora_no_nome(self):
        backup = fazer_backup(self.destino, agora=datetime(2026, 11, 5, 14, 30, 7))

        self.assertEqual(list(self.destino.iterdir()), [backup])
        self.assertEqual(backup.name, 'backup-comparador-2026-11-05_14-30-07.zip')

    def test_restaurar_numa_instalacao_vazia_traz_de_volta_a_oferta_com_o_preco_e_o_arquivo_de_origem(self):
        conteudo_de_origem = self.importar_catalogo()
        backup = fazer_backup(self.destino)
        self.apagar_a_instalacao()

        restaurar_backup(backup)

        gestora = Gestor.objects.get(username='gestora')
        [oferta] = buscar_ofertas(gestora, '1001').ofertas
        self.assertEqual((oferta.codigo, oferta.descricao, oferta.preco_unitario), ('1001', 'Balde Ficticio', Decimal('9.90')))
        with oferta.catalogo.arquivo.open('rb') as arquivo_de_origem:
            self.assertEqual(arquivo_de_origem.read(), conteudo_de_origem)

    def test_arquivo_posto_em_fotos_volta_com_o_mesmo_conteudo(self):
        # A foto de uma Oferta de verdade só existe a partir do ticket 14, que repete este teste com ela.
        self.importar_catalogo()
        conteudo_da_foto = b'\xff\xd8\xff\xe0 foto ficticia \xff\xd9'
        (self.pasta_de_arquivos / 'fotos').mkdir()
        (self.pasta_de_arquivos / 'fotos' / '3f9a1c.jpg').write_bytes(conteudo_da_foto)
        backup = fazer_backup(self.destino)
        self.apagar_a_instalacao()

        restaurar_backup(backup)

        self.assertEqual((self.pasta_de_arquivos / 'fotos' / '3f9a1c.jpg').read_bytes(), conteudo_da_foto)
