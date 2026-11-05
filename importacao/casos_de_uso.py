"""Casos de uso do módulo Importação e Revisão. As telas e os testes entram por aqui."""

import re
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from catalogos.casos_de_uso import conteudo_digitado, guardar_conteudo, registrar_catalogo
from comparador.erros import AcessoNegado, ErroDeNegocio
from extracao.extrair import extrair_catalogo
from importacao.models import OfertaProposta, Revisao


def iniciar_importacao(gestor, fornecedor, arquivo, hoje=None):
    """`hoje` é injetável para os testes simularem dias diferentes; o padrão é o dia local."""
    if fornecedor is None:
        raise ErroDeNegocio('Escolha o Fornecedor do Catálogo.')
    if arquivo is None:
        raise ErroDeNegocio('Escolha o arquivo do Catálogo.')
    extracao = extrair_catalogo(arquivo)
    ofertas = extracao.ofertas
    arquivo.seek(0)
    with transaction.atomic():
        revisao = Revisao.objects.create(
            gestor=gestor,
            fornecedor=fornecedor,
            arquivo=arquivo,
            iniciada_em=hoje or timezone.localdate(),
            precos_no_arquivo=extracao.precos_no_arquivo,
            ofertas_extraidas=len(ofertas),
        )
        OfertaProposta.objects.bulk_create(
            OfertaProposta(
                revisao=revisao,
                ordem=ordem,
                codigo=oferta.codigo,
                descricao=oferta.descricao,
                preco_impresso=oferta.preco_impresso,
                caixa=oferta.caixa,
                caminho=oferta.caminho,
            )
            for ordem, oferta in enumerate(ofertas)
        )
    return revisao


def informar_condicoes_do_catalogo(gestor, revisao_id, desconto):
    """`desconto` é o percentual como a gestora digitou (ex.: "3" ou "2,5")."""
    revisao = _revisao_em_andamento(gestor, revisao_id)
    revisao.desconto = _desconto_valido(desconto)
    revisao.save()


def corrigir_oferta_proposta(gestor, oferta_id, codigo, descricao, preco_impresso, caixa, conteudo):
    """Os valores chegam como a gestora digitou: preço "1.234,56" ou "9,90"; Caixa "24"; vazio = ausente.

    O Conteúdo definido aqui fica só na Revisão até a confirmação.
    """
    oferta = _oferta_proposta_em_andamento(gestor, oferta_id)
    oferta.codigo, oferta.descricao = _codigo_e_descricao(codigo, descricao)
    oferta.preco_impresso = _preco_digitado(preco_impresso)
    oferta.caixa = _caixa_digitada(caixa)
    oferta.conteudo_definido = conteudo_digitado(conteudo)
    oferta.save()


def aceitar_sugestao_de_conteudo(gestor, oferta_id):
    """Aceitar a sugestão é definir o Conteúdo na Revisão (ticket 07): só fica guardado ao confirmar.

    Sem sugestão (já aceita, por exemplo), não faz nada.
    """
    oferta = _oferta_proposta_em_andamento(gestor, oferta_id)
    sugestao = oferta.sugestao_de_conteudo
    if sugestao is None:
        return
    corrigir_oferta_proposta(
        gestor,
        oferta_id,
        codigo=oferta.codigo,
        descricao=oferta.descricao,
        preco_impresso='' if oferta.preco_impresso is None else str(oferta.preco_impresso),
        caixa='' if oferta.caixa is None else str(oferta.caixa),
        conteudo=str(sugestao),
    )


CAMINHO_MANUAL = 'manual'


def adicionar_oferta_proposta(gestor, revisao_id, codigo, descricao, preco_impresso, caixa):
    """Oferta digitada pela gestora, para um item que a extração não encontrou (história 35)."""
    revisao = _revisao_em_andamento(gestor, revisao_id)
    codigo, descricao = _codigo_e_descricao(codigo, descricao)
    ultima = revisao.ofertas.order_by('-ordem').first()
    return OfertaProposta.objects.create(
        revisao=revisao,
        ordem=ultima.ordem + 1 if ultima else 0,
        codigo=codigo,
        descricao=descricao,
        preco_impresso=_preco_digitado(preco_impresso),
        caixa=_caixa_digitada(caixa),
        caminho=CAMINHO_MANUAL,
    )


def remover_oferta_proposta(gestor, oferta_id):
    _oferta_proposta_em_andamento(gestor, oferta_id).delete()


def _codigo_e_descricao(codigo, descricao):
    """Oferta sem código ou sem descrição não pode existir: o código liga Conteúdo e Produto."""
    codigo, descricao = codigo.strip(), descricao.strip()
    if not codigo or not descricao:
        raise ErroDeNegocio('Informe o código e a descrição da Oferta.')
    return codigo, descricao


# Sem vírgula, um ponto seguido de exatamente 3 dígitos parece separador de milhar.
PONTO_DE_MILHAR = re.compile(r'\.\d{3}(?!\d)')


def _preco_digitado(texto):
    texto = texto.strip()
    if not texto:
        return None
    if ',' in texto:  # formato brasileiro: ponto separa milhar, vírgula separa centavos
        texto = texto.replace('.', '').replace(',', '.')
    elif PONTO_DE_MILHAR.search(texto):  # "1.500" pode ser mil e quinhentos ou 1,50: ambíguo
        raise ErroDeNegocio(
            'Use vírgula para os centavos: 1.500,00 para mil e quinhentos, 1,50 para um real e cinquenta.'
        )
    try:
        preco = Decimal(texto)
    except InvalidOperation:
        preco = None
    if preco is None or not preco.is_finite() or preco <= 0:
        raise ErroDeNegocio('O preço precisa ser maior que zero.')
    return preco


def _caixa_digitada(texto):
    texto = texto.strip()
    if not texto:
        return None
    if not texto.isdecimal() or int(texto) == 0:  # isdecimal: só o que int() lê ("³" não)
        raise ErroDeNegocio('A Caixa precisa ser um número inteiro de Unidades de venda, maior que zero.')
    return int(texto)


def _desconto_valido(texto):
    try:
        desconto = Decimal(texto.strip().replace(',', '.'))
    except InvalidOperation:
        desconto = None
    if desconto is None or not desconto.is_finite() or not 0 <= desconto < 100:
        raise ErroDeNegocio('O desconto precisa ser de 0% até menos de 100%.')
    return desconto


def confirmar_revisao(gestor, revisao_id, hoje=None):
    """`hoje` é o dia registrado no histórico do Conteúdo; injetável nos testes."""
    revisao = _revisao_em_andamento(gestor, revisao_id)
    ofertas = revisao.ofertas_propostas()
    _exigir_revisao_completa(revisao, ofertas)
    # O Catálogo aponta para o mesmo arquivo guardado na Revisão: ele vira o arquivo de origem.
    # Transação única: se uma Oferta falhar, nem o Catálogo nem a marcação da Revisão ficam salvos.
    with transaction.atomic():
        catalogo = registrar_catalogo(
            gestor,
            revisao.fornecedor,
            revisao.iniciada_em,
            revisao.arquivo,
            revisao.desconto,
            ofertas,
        )
        for oferta in ofertas:
            if oferta.conteudo_definido is not None:
                guardar_conteudo(
                    gestor, revisao.fornecedor, oferta.codigo, oferta.conteudo_definido, hoje or timezone.localdate()
                )
        revisao.catalogo = catalogo
        revisao.save()
    return catalogo


def _exigir_revisao_completa(revisao, ofertas):
    """Recusa a confirmação listando, de uma vez, tudo o que falta (spec, Revisão)."""
    problemas = []
    if revisao.desconto is None:
        # O desconto é resposta obrigatória a cada Importação; 0 vale (decisão da usuária, ticket 06).
        problemas.append('Informe o desconto do Catálogo antes de confirmar. Se não houver desconto, informe 0.')
    sem_caixa = [oferta.codigo for oferta in ofertas if oferta.caixa is None]
    if sem_caixa:
        problemas.append(f'Informe a Caixa antes de confirmar. Ofertas sem Caixa: {", ".join(sem_caixa)}.')
    sem_preco = [oferta.codigo for oferta in ofertas if oferta.preco_impresso is None or oferta.preco_impresso <= 0]
    if sem_preco:
        problemas.append(
            f'Informe um preço maior que zero antes de confirmar. Ofertas sem preço: {", ".join(sem_preco)}.'
        )
    if problemas:
        raise ErroDeNegocio(' '.join(problemas))


def abandonar_revisao(gestor, revisao_id):
    # Uma Revisão confirmada também é recusada: o arquivo dela agora é o arquivo de origem do
    # Catálogo (decisão da usuária no ticket 04).
    revisao = _revisao_em_andamento(gestor, revisao_id)
    arquivo = revisao.arquivo
    revisao.delete()  # leva junto as Ofertas propostas
    arquivo.delete(save=False)


def listar_revisoes_em_andamento(gestor):
    return Revisao.objects.filter(gestor=gestor, catalogo__isnull=True)


def obter_revisao(gestor, revisao_id):
    # A Revisão em andamento é de quem iniciou a Importação (decisão da usuária no ticket 03).
    revisao = Revisao.objects.get(pk=revisao_id)
    if revisao.gestor_id != gestor.pk:
        raise AcessoNegado('Esta Revisão é de outro Gestor.')
    return revisao


def obter_oferta_proposta(gestor, oferta_id):
    """Para os formulários de Corrigir e Remover: mesmas recusas de quem altera a Revisão."""
    return _oferta_proposta_em_andamento(gestor, oferta_id)


def _oferta_proposta_em_andamento(gestor, oferta_id):
    """A Oferta proposta de uma Revisão do Gestor que ainda está em andamento."""
    oferta = OfertaProposta.objects.filter(pk=oferta_id).first()
    if oferta is None:
        raise ErroDeNegocio('Esta Oferta não existe mais na Revisão.')
    _revisao_em_andamento(gestor, oferta.revisao_id)
    return oferta


def _revisao_em_andamento(gestor, revisao_id):
    """A Revisão do Gestor que ainda pode ser confirmada ou abandonada."""
    revisao = Revisao.objects.filter(pk=revisao_id).first()
    if revisao is None:
        raise ErroDeNegocio('Esta Revisão não existe mais. Comece uma nova Importação.')
    if revisao.gestor_id != gestor.pk:
        raise AcessoNegado('Esta Revisão é de outro Gestor.')
    if revisao.catalogo_id is not None:
        raise ErroDeNegocio('Esta Revisão já foi confirmada.')
    return revisao
