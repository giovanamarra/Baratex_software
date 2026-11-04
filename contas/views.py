"""Telas do módulo Contas. São finas: só chamam os casos de uso."""

from django.shortcuts import render

from contas.casos_de_uso import listar_minhas_lojas


def inicio(request):
    return render(request, 'contas/inicio.html', {'lojas': listar_minhas_lojas(request.user)})
