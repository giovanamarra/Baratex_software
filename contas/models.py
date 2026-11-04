from django.contrib.auth.models import AbstractUser
from django.db import models


class Gestor(AbstractUser):
    """Pessoa do grupo que compra para as próprias Lojas (GLOSSARY)."""

    class Meta:
        verbose_name = 'Gestor'
        verbose_name_plural = 'Gestores'


class Loja(models.Model):
    """Unidade do grupo para a qual se compra mercadoria. Pertence a um Gestor (ADR-0007)."""

    nome = models.CharField(max_length=200)
    gestor = models.ForeignKey(Gestor, on_delete=models.PROTECT, related_name='lojas')

    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'

    def __str__(self):
        return self.nome
