"""Telas do módulo Catálogos. São finas: só chamam os casos de uso."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from catalogos.casos_de_uso import (
    LIMITE_DE_RESULTADOS,
    buscar_ofertas,
    cadastrar_fornecedor,
    definir_conteudo,
    historico_do_conteudo,
    listar_catalogos_do_fornecedor,
    listar_fornecedores,
    obter_catalogo,
    obter_oferta,
)
from catalogos.models import Catalogo, Oferta
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


def buscar(request):
    """Busca nos Catálogos de todos os Fornecedores. A tela só chama o caso de uso; sem parâmetros, só mostra o formulário."""
    fornecedores = listar_fornecedores(request.user).order_by('nome')
    texto = request.GET.get('texto', '')
    fornecedor_escolhido = request.GET.get('fornecedor', '')
    antigas = request.GET.get('antigas') == '1'
    contexto = {
        'fornecedores': fornecedores, 'texto': texto, 'fornecedor_escolhido': fornecedor_escolhido,
        'antigas': antigas, 'limite': LIMITE_DE_RESULTADOS, 'voltar': request.get_full_path(),
    }
    if request.GET:
        fornecedor = fornecedores.filter(pk=fornecedor_escolhido).first() if fornecedor_escolhido.isdecimal() else None
        try:
            contexto['resultado'] = buscar_ofertas(request.user, texto, fornecedor=fornecedor, so_vigentes=not antigas)
        except ErroDeNegocio as erro:
            contexto['erro'] = erro.mensagem
    return render(request, 'catalogos/buscar.html', contexto)


def catalogos_do_fornecedor(request, pk):
    fornecedor = listar_fornecedores(request.user).filter(pk=pk).first()
    if fornecedor is None:
        raise Http404
    catalogos = listar_catalogos_do_fornecedor(request.user, fornecedor).select_related('gestor')
    return render(
        request, 'catalogos/catalogos_do_fornecedor.html', {'fornecedor': fornecedor, 'catalogos': catalogos}
    )


def catalogo(request, pk):
    try:
        catalogo = obter_catalogo(request.user, pk)
    except Catalogo.DoesNotExist:
        raise Http404
    return render(request, 'catalogos/catalogo.html', {'catalogo': catalogo, 'ofertas': catalogo.ofertas()})


def definir_conteudo_da_oferta(request, pk):
    """Fora da Revisão: o Conteúdo vale para o Fornecedor + código da Oferta, em todos os Catálogos."""
    oferta = _oferta(request, pk)
    contexto = {'oferta': oferta, 'conteudo': str(oferta.conteudo), 'voltar_para': _para_onde_voltar(request)}
    if request.method == 'POST':
        contexto['conteudo'] = request.POST.get('conteudo', '')
        try:
            definir_conteudo(request.user, oferta.catalogo.fornecedor, oferta.codigo, contexto['conteudo'])
        except ErroDeNegocio as erro:
            contexto['erro'] = erro.mensagem
        else:
            messages.success(request, f'Conteúdo do código {oferta.codigo} agora é {contexto["conteudo"].strip()}.')
            return redirect(_para_onde_voltar(request) or reverse('catalogo', kwargs={'pk': oferta.catalogo_id}))
    return render(request, 'catalogos/definir_conteudo.html', contexto)


def _para_onde_voltar(request):
    """Endereço de onde a gestora veio (`voltar`), se for do próprio sistema; senão, vazio."""
    voltar = request.GET.get('voltar', '')
    if voltar and url_has_allowed_host_and_scheme(voltar, allowed_hosts={request.get_host()}):
        return voltar
    return ''


def historico_do_conteudo_da_oferta(request, pk):
    oferta = _oferta(request, pk)
    alteracoes = historico_do_conteudo(request.user, oferta.catalogo.fornecedor, oferta.codigo).select_related('gestor')
    return render(request, 'catalogos/historico_do_conteudo.html', {'oferta': oferta, 'alteracoes': alteracoes})


def _oferta(request, pk):
    try:
        return obter_oferta(request.user, pk)
    except Oferta.DoesNotExist:
        raise Http404
