"""Telas do módulo Catálogos. São finas: só chamam os casos de uso."""

from django.shortcuts import redirect, render

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_fornecedores
from comparador.erros import ErroDeNegocio


def fornecedores(request):
    contexto = {'nome': ''}
    if request.method == 'POST':
        nome = request.POST.get('nome', '')
        try:
            cadastrar_fornecedor(request.user, nome)
            return redirect('fornecedores')
        except ErroDeNegocio as erro:
            contexto = {'nome': nome, 'erro': erro.mensagem}
    contexto['fornecedores'] = listar_fornecedores(request.user).order_by('nome')
    return render(request, 'catalogos/fornecedores.html', contexto)
