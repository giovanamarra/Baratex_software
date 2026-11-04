"""Casos de uso do módulo Catálogos. As telas e os testes entram por aqui."""

from catalogos.models import Fornecedor
from comparador.erros import ErroDeNegocio


def cadastrar_fornecedor(gestor, nome):
    nome = nome.strip()
    if not nome:
        raise ErroDeNegocio('Informe o nome do Fornecedor.')
    return Fornecedor.objects.create(nome=nome)


def listar_fornecedores(gestor):
    return Fornecedor.objects.all()
