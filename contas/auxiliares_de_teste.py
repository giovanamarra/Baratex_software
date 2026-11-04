"""Auxiliares reutilizados pelos testes de todos os módulos."""

from contas.models import Gestor, Loja

SENHA_DE_TESTE = 'senha-de-teste'


def criar_gestor(usuario='gestora'):
    return Gestor.objects.create_user(username=usuario, password=SENHA_DE_TESTE)


def criar_loja(gestor, nome):
    # Na aplicação, Lojas são cadastradas pelo painel administrativo.
    return Loja.objects.create(gestor=gestor, nome=nome)


def nomes(objetos):
    return [objeto.nome for objeto in objetos]
