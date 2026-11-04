"""Casos de uso do módulo Catálogos. As telas e os testes entram por aqui."""

from catalogos.models import Fornecedor


def cadastrar_fornecedor(gestor, nome):
    return Fornecedor.objects.create(nome=nome.strip())


def listar_fornecedores(gestor):
    return Fornecedor.objects.all()
