from django.db import models


class Fornecedor(models.Model):
    """Empresa que vende produtos ao grupo (GLOSSARY). Pertence ao grupo (ADR-0007)."""

    nome = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.nome
