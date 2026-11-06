"""Catálogos de antes do ADR-0009 ganham a data do Catálogo completa igual ao dia da Importação (ticket 31)."""

from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

ANTES_DO_TICKET_31 = ('catalogos', '0011_teto_de_compra')


class MigracaoDaDataDoCatalogoTests(TransactionTestCase):
    def migrar(self, alvos):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(alvos)
        return executor.loader.project_state(alvos).apps

    def ate_o_fim(self):
        return MigrationExecutor(connection).loader.graph.leaf_nodes()

    def test_catalogo_antigo_ganha_data_completa_igual_ao_dia_da_importacao(self):
        self.addCleanup(self.migrar, self.ate_o_fim())  # devolve o banco de teste ao estado atual
        apps = self.migrar([ANTES_DO_TICKET_31])
        gestora = apps.get_model('contas', 'Gestor').objects.create(username='gestora')
        fornecedor = apps.get_model('catalogos', 'Fornecedor').objects.create(nome='Fornecedor Alfa')
        # No formato antigo, `data` era o dia em que a Importação começou.
        antigo = apps.get_model('catalogos', 'Catalogo').objects.create(
            fornecedor=fornecedor, gestor=gestora, arquivo='importacoes/2026/03/catalogo.pdf', data=date(2026, 3, 2)
        )

        apps = self.migrar(self.ate_o_fim())

        migrado = apps.get_model('catalogos', 'Catalogo').objects.get(pk=antigo.pk)
        self.assertEqual(
            (migrado.data, migrado.data_so_mes_e_ano, migrado.importado_em),
            (date(2026, 3, 2), False, date(2026, 3, 2)),
        )
