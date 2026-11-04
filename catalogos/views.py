"""Telas do módulo Catálogos. São finas: só chamam os casos de uso."""

from django.http import Http404
from django.shortcuts import redirect, render

from catalogos.casos_de_uso import cadastrar_fornecedor, listar_catalogos_do_fornecedor, listar_fornecedores
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


def catalogos_do_fornecedor(request, pk):
    fornecedor = listar_fornecedores(request.user).filter(pk=pk).first()
    if fornecedor is None:
        raise Http404
    catalogos = listar_catalogos_do_fornecedor(request.user, fornecedor).select_related('gestor')
    return render(
        request, 'catalogos/catalogos_do_fornecedor.html', {'fornecedor': fornecedor, 'catalogos': catalogos}
    )
