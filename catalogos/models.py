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

    class Meta:
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogos'
