"""Telas do módulo Importação e Revisão. São finas: só chamam os casos de uso."""

from django.http import Http404
from django.shortcuts import redirect, render

from catalogos.casos_de_uso import listar_fornecedores
from comparador.erros import AcessoNegado, ErroDeNegocio
from importacao.casos_de_uso import iniciar_importacao, listar_revisoes_em_andamento, obter_revisao
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
        return render(request, 'acesso_negado.html', {'mensagem': erro.mensagem}, status=403)
    return render(request, 'importacao/revisao.html', {'revisao': revisao, 'ofertas': revisao.ofertas_propostas()})
