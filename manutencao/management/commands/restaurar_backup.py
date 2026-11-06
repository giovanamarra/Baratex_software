from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from comparador.erros import ErroDeNegocio
from manutencao.casos_de_uso import restaurar_backup


class Command(BaseCommand):
    help = 'Restaura um backup do Comparador de Catálogos numa instalação vazia.'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', help='O arquivo .zip gerado por fazer_backup.')

    def handle(self, *args, arquivo, **opcoes):
        try:
            restaurar_backup(arquivo)
        except ErroDeNegocio as erro:
            raise CommandError(erro.mensagem)
        self.stdout.write(f'Pronto: backup {Path(arquivo).name} restaurado.')
