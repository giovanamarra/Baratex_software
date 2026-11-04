"""Telas do módulo Contas. São finas: só chamam os casos de uso."""

from django.shortcuts import render


def inicio(request):
    return render(request, 'contas/inicio.html')
