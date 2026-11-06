from django.core.management.base import BaseCommand

from manutencao.casos_de_uso import fazer_backup


class Command(BaseCommand):
    help = 'Grava, na pasta indicada, um único .zip com o banco e a pasta de arquivos inteira.'

    def add_arguments(self, parser):
        parser.add_argument('pasta', help='Pasta onde o backup será gravado (por exemplo, o pendrive).')

    def handle(self, *args, pasta, **opcoes):
        backup = fazer_backup(pasta)
        self.stdout.write(f'Pronto: backup gravado em {backup}')
