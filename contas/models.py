from django.contrib.auth.models import AbstractUser


class Gestor(AbstractUser):
    """Pessoa do grupo que compra para as próprias Lojas (GLOSSARY)."""

    class Meta:
        verbose_name = 'Gestor'
        verbose_name_plural = 'Gestores'
