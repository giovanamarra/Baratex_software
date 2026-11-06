from django.db import migrations, models


def dia_da_importacao_dos_catalogos_existentes(apps, schema_editor):
    """Antes do ADR-0009, `data` era o dia da Importação. Ele vira o registro do dia da Importação, e a data do
    Catálogo fica a mesma data completa: nenhuma Oferta vigente muda (spec, Catálogos já existentes)."""
    Catalogo = apps.get_model('catalogos', 'Catalogo')
    Catalogo.objects.filter(importado_em__isnull=True).update(importado_em=models.F('data'))


class Migration(migrations.Migration):
    dependencies = [
        ('catalogos', '0012_data_do_catalogo_e_dia_da_importacao'),
    ]

    operations = [
        migrations.RunPython(dia_da_importacao_dos_catalogos_existentes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='catalogo',
            name='importado_em',
            field=models.DateField(),
        ),
    ]
