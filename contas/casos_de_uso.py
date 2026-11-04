"""Casos de uso do módulo Contas. As telas e os testes entram por aqui."""

from contas.models import Loja


def listar_minhas_lojas(gestor):
    return Loja.objects.filter(gestor=gestor)
