"""Casos de uso do módulo Contas. As telas e os testes entram por aqui."""

from comparador.erros import ErroDeNegocio
from contas.models import Loja


def listar_minhas_lojas(gestor):
    return Loja.objects.filter(gestor=gestor)


def renomear_loja(gestor, loja, nome):
    if loja.gestor_id != gestor.pk:
        raise ErroDeNegocio('Esta Loja é de outro Gestor. Só ele pode editá-la.')
    loja.nome = nome
    loja.save()
