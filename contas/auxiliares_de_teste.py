"""Auxiliares reutilizados pelos testes de todos os módulos."""

from contas.models import Gestor


def criar_gestor(usuario='gestora'):
    return Gestor.objects.create_user(username=usuario, password='senha-de-teste')
