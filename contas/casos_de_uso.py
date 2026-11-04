"""Casos de uso do módulo Contas. As telas e os testes entram por aqui."""

from comparador.erros import AcessoNegado, ErroDeNegocio
from contas.models import Loja


def listar_minhas_lojas(gestor):
    return Loja.objects.filter(gestor=gestor)


def exigir_dono_da_loja(gestor, loja):
    if loja.gestor_id != gestor.pk:
        raise AcessoNegado('Esta Loja é de outro Gestor. Só ele pode editá-la.')


def renomear_loja(gestor, loja, nome):
    exigir_dono_da_loja(gestor, loja)
    nome = nome.strip()
    if not nome:
        raise ErroDeNegocio('Informe o nome da Loja.')
    loja.nome = nome
    loja.save()
