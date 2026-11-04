from django.conf import settings
from django.db import models


class Fornecedor(models.Model):
    """Empresa que vende produtos ao grupo (GLOSSARY). Pertence ao grupo (ADR-0007)."""

    nome = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.nome


class Catalogo(models.Model):
    """Conjunto de preços de um Fornecedor, datado pelo dia da Importação. Nunca é sobrescrito."""

    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='catalogos')
    gestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='catalogos_importados')
    arquivo = models.FileField(upload_to='importacoes/%Y/%m/')
    data = models.DateField()  # dia em que a Importação começou

    class Meta:
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogos'

    def ofertas(self):
        return list(self.ofertas_do_catalogo.order_by('ordem'))


class Oferta(models.Model):
    """Um item de um Catálogo: algo que o Fornecedor propõe vender, com o preço daquele Catálogo."""

    catalogo = models.ForeignKey(Catalogo, on_delete=models.PROTECT, related_name='ofertas_do_catalogo')
    ordem = models.PositiveIntegerField()
    codigo = models.CharField(max_length=100)
    descricao = models.CharField(max_length=300)
    preco_impresso = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    caixa = models.PositiveIntegerField(null=True)
    caminho = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
