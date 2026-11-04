"""Telas do módulo Contas. São finas: só chamam os casos de uso."""

from django.shortcuts import get_object_or_404, redirect, render

from comparador.erros import AcessoNegado, ErroDeNegocio
from contas.casos_de_uso import exigir_dono_da_loja, listar_minhas_lojas, renomear_loja
from contas.models import Loja


def inicio(request):
    return render(request, 'contas/inicio.html', {'lojas': listar_minhas_lojas(request.user)})


def editar_loja(request, pk):
    loja = get_object_or_404(Loja, pk=pk)
    nome = request.POST.get('nome', '') if request.method == 'POST' else loja.nome
    try:
        if request.method == 'POST':
            renomear_loja(request.user, loja, nome)
            return redirect('inicio')
        exigir_dono_da_loja(request.user, loja)
    except AcessoNegado as erro:
        return render(request, 'acesso_negado.html', {'mensagem': erro.mensagem}, status=403)
    except ErroDeNegocio as erro:
        contexto = {'loja': loja, 'nome': nome, 'erro': erro.mensagem}
        return render(request, 'contas/editar_loja.html', contexto)
    return render(request, 'contas/editar_loja.html', {'loja': loja, 'nome': nome})
