"""Telas do módulo Importação e Revisão. São finas: só chamam os casos de uso."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from catalogos.casos_de_uso import listar_fornecedores
from comparador.erros import AcessoNegado, ErroDeNegocio
from importacao.casos_de_uso import (
    abandonar_revisao,
    aceitar_sugestao_de_conteudo,
    adicionar_oferta_proposta,
    confirmar_revisao,
    corrigir_oferta_proposta,
    informar_condicoes_do_catalogo,
    informar_data_do_catalogo,
    iniciar_importacao,
    listar_revisoes_em_andamento,
    manter_conteudo_1,
    obter_oferta_proposta,
    obter_revisao,
    remover_oferta_proposta,
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
def informar_condicoes(request, pk):
    try:
        informar_condicoes_do_catalogo(request.user, pk, request.POST.get('desconto', ''))
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
    return redirect('revisao', pk=pk)


@require_POST
def informar_data(request, pk):
    # O atalho "É de hoje" envia, pelo mesmo caminho, o dia em que a Importação começou.
    try:
        informar_data_do_catalogo(request.user, pk, request.POST.get('data', ''))
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
    return redirect('revisao', pk=pk)


@require_POST
def confirmar(request, pk):
    try:
        catalogo = confirmar_revisao(request.user, pk)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
        # Se a Revisão ainda está em andamento (faltou Caixa, preço ou desconto), volta para corrigi-la.
        if listar_revisoes_em_andamento(request.user).filter(pk=pk).exists():
            return redirect('revisao', pk=pk)
        return redirect('importar')
    messages.success(request, f'Revisão confirmada: Catálogo de {catalogo.data_exibida} salvo.')
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


CAMPOS_DA_OFERTA = ('codigo', 'descricao', 'preco_impresso', 'caixa')


def corrigir_oferta(request, pk):
    try:
        oferta = obter_oferta_proposta(request.user, pk)
        if request.method == 'POST':
            valores = _valores_digitados(request)
            valores['conteudo'] = request.POST.get('conteudo', '')
            try:
                corrigir_oferta_proposta(request.user, pk, **valores)
            except AcessoNegado:
                raise
            except ErroDeNegocio as erro:
                return _formulario_da_oferta(request, oferta.revisao, valores, erro.mensagem, oferta)
            messages.success(request, f'Oferta {valores["codigo"].strip()} corrigida.')
            return redirect('revisao', pk=oferta.revisao_id)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
        return redirect('importar')
    valores = {
        'codigo': oferta.codigo,
        'descricao': oferta.descricao,
        'preco_impresso': '' if oferta.preco_impresso is None else f'{oferta.preco_impresso:.2f}'.replace('.', ','),
        'caixa': '' if oferta.caixa is None else str(oferta.caixa),
        'conteudo': str(oferta.conteudo),
    }
    return _formulario_da_oferta(request, oferta.revisao, valores, None, oferta)


def adicionar_oferta(request, pk):
    try:
        revisao = obter_revisao(request.user, pk)
        if revisao.catalogo_id:
            raise ErroDeNegocio('Esta Revisão já foi confirmada.')
        if request.method == 'POST':
            valores = _valores_digitados(request)
            try:
                adicionar_oferta_proposta(request.user, pk, **valores)
            except AcessoNegado:
                raise
            except ErroDeNegocio as erro:
                return _formulario_da_oferta(request, revisao, valores, erro.mensagem)
            messages.success(request, f'Oferta {valores["codigo"].strip()} adicionada.')
            return redirect('revisao', pk=pk)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except (ErroDeNegocio, Revisao.DoesNotExist) as erro:
        messages.error(request, getattr(erro, 'mensagem', 'Esta Revisão não existe mais. Comece uma nova Importação.'))
        return redirect('importar')
    return _formulario_da_oferta(request, revisao, dict.fromkeys(CAMPOS_DA_OFERTA, ''), None)


def remover_oferta(request, pk):
    # GET mostra a confirmação (ação destrutiva, BRAND.md); POST remove de fato.
    try:
        oferta = obter_oferta_proposta(request.user, pk)
        if request.method == 'POST':
            remover_oferta_proposta(request.user, pk)
            messages.success(request, f'Oferta {oferta.codigo} removida da Revisão.')
            return redirect('revisao', pk=oferta.revisao_id)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
        return redirect('importar')
    return render(request, 'importacao/remover_oferta.html', {'oferta': oferta})


@require_POST
def aceitar_sugestao(request, pk):
    return _decidir_sugestao(request, pk, aceitar_sugestao_de_conteudo, 'Sugestão de Conteúdo aceita para a Oferta {}.')


@require_POST
def manter_1(request, pk):
    return _decidir_sugestao(request, pk, manter_conteudo_1, 'Conteúdo 1 mantido para a Oferta {}.')


def _decidir_sugestao(request, pk, caso_de_uso, aviso):
    """Aceitar ou Manter 1: a decisão fica na Revisão e só é guardada ao confirmar (ticket 07)."""
    try:
        oferta = obter_oferta_proposta(request.user, pk)
        caso_de_uso(request.user, pk)
    except AcessoNegado as erro:
        return _acesso_negado(request, erro)
    except ErroDeNegocio as erro:
        messages.error(request, erro.mensagem)
        return redirect('importar')
    messages.success(request, aviso.format(oferta.codigo))
    return redirect('revisao', pk=oferta.revisao_id)


def _valores_digitados(request):
    return {campo: request.POST.get(campo, '') for campo in CAMPOS_DA_OFERTA}


def _formulario_da_oferta(request, revisao, valores, erro, oferta=None):
    contexto = {'revisao': revisao, 'valores': valores, 'erro': erro, 'oferta': oferta}
    return render(request, 'importacao/oferta_proposta.html', contexto)


def _acesso_negado(request, erro):
    return render(request, 'acesso_negado.html', {'mensagem': erro.mensagem}, status=403)
