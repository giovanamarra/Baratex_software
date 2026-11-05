import unicodedata

from django.db import migrations


def _normalizar(texto):
    # Cópia de catalogos.busca.normalizar de quando a migração foi escrita: migração não importa código vivo.
    decomposto = unicodedata.normalize('NFKD', texto.casefold())
    return ''.join(c for c in decomposto if not unicodedata.combining(c))


def preencher_busca(apps, schema_editor):
    Oferta = apps.get_model('catalogos', 'Oferta')
    pendentes = []
    for oferta in Oferta.objects.only('pk', 'codigo', 'descricao').iterator(chunk_size=2000):
        oferta.busca = _normalizar(f'{oferta.codigo}\n{oferta.descricao}')
        pendentes.append(oferta)
        if len(pendentes) == 2000:
            Oferta.objects.bulk_update(pendentes, ['busca'])
            pendentes = []
    Oferta.objects.bulk_update(pendentes, ['busca'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0008_oferta_busca'),
    ]

    operations = [
        migrations.RunPython(preencher_busca, migrations.RunPython.noop),
    ]
