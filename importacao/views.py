"""Telas do módulo Importação e Revisão. São finas: só chamam os casos de uso."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from catalogos.casos_de_uso import listar_fornecedores
from comparador.erros import AcessoNegado, ErroDeNegocio
from importacao.casos_de_uso import (
    abandonar_revisao,
    confirmar_revisao,
    iniciar_importacao,
    listar_revisoes_em_andamento,
    obter_revisao,
)
from importacao.models import Revisao


def importar(request):
    contexto = {}
    if request.method == 'POST':
        fornecedor_id = request.POST.get('fornecedor') or None
        fornecedor = listar_fornecedores(request.user).filter(pk=fornecedor_id).first() if fornecedor_id else None
        try:
            revisao = iniciar_importacao(request.user, fornecedor, request.FILES.get('arquivo'))
            return redirect('revisao', pk=revisao.pk)
        except ErroDeNegocio as erro:
            contexto = {'erro': erro.mensagem, 'fornecedor_escolhido': fornecedor_id}
    contexto['fornecedores'] = listar_fornecedores(request.user).order_by('nome')
    contexto['revisoes'] = listar_revisoes_em_andamento(request.user).select_related('fornecedor')
    return render(request, 'importacao/importar.html', contexto)


def revisao(request, pk):
    try:
        revisao = obter_revisao(request.user, pk)
    except Revisao.DoesNotExist:
        raise Http404
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    return render(request, 'importacao/revisao.html', {'revisao': revisao, 'ofertas': revisao.ofertas_propostas()})


@require_POST
def confirmar(request, pk):
    try:
        catalogo = confirmar_revisao(request.user, pk)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
        return redirect('importar')
    messages.success(request, f'Revisão confirmada: Catálogo de {catalogo.data:%d/%m/%Y} salvo.')
    return redirect('catalogos_do_fornecedor', pk=catalogo.fornecedor_id)


def abandonar(request, pk):
    # GET mostra a confirmação (abandonar apaga o arquivo); POST abandona de fato.
    try:
        if request.method == 'POST':
            abandonar_revisao(request.user, pk)
            messages.success(request, 'Revisão abandonada. O arquivo enviado foi apagado e nada foi salvo.')
            return redirect('importar')
        revisao = obter_revisao(request.user, pk)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except (ErroDeNegocio, Revisao.DoesNotExist) as erro:
        messages.error(request, getattr(erro, 'mensagem', 'Esta Revisão não existe mais. Comece uma nova Importação.'))
        return redirect('importar')
    return render(request, 'importacao/abandonar.html', {'revisao': revisao})


def _acesso_negado(request, erro):
    return render(request, 'acesso_negado.html', {'mensagem': erro.mensagem}, status=403)
