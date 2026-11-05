"""Casos de uso do módulo Catálogos. As telas e os testes entram por aqui."""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from django.db.models import DecimalField, Exists, ExpressionWrapper, F, OuterRef, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from catalogos.busca import normalizar, texto_de_busca
from catalogos.models import (
    AlteracaoDeConteudo,
    Catalogo,
    Fornecedor,
    Oferta,
    TetoDeCompra,
    conteudo_guardado,
    conteudos_guardados,
    teto_atual,
)
from comparador.erros import ErroDeNegocio


def cadastrar_fornecedor(gestor, nome):
    nome = nome.strip()
    if not nome:
        raise ErroDeNegocio('Informe o nome do Fornecedor.')
    existente = _fornecedor_com_o_mesmo_nome(nome)
    if existente:
        raise ErroDeNegocio(f'Já existe um Fornecedor chamado {existente.nome}.')
    return Fornecedor.objects.create(nome=nome)


def listar_fornecedores(gestor):
    return Fornecedor.objects.all()


def registrar_catalogo(gestor, fornecedor, data, arquivo, desconto, ofertas):
    """Cria o Catálogo e as suas Ofertas. Chamado pela Importação ao confirmar a Revisão."""
    catalogo = Catalogo.objects.create(
        gestor=gestor, fornecedor=fornecedor, data=data, arquivo=arquivo, desconto=desconto
    )
    Oferta.objects.bulk_create(
        Oferta(
            catalogo=catalogo,
            ordem=ordem,
            codigo=oferta.codigo,
            descricao=oferta.descricao,
            preco_impresso=oferta.preco_impresso,
            caixa=oferta.caixa,
            caminho=oferta.caminho,
            busca=texto_de_busca(oferta.codigo, oferta.descricao),
        )
        for ordem, oferta in enumerate(ofertas)
    )
    return catalogo


def guardar_conteudo(gestor, fornecedor, codigo, conteudo, hoje, decisao_explicita=False):
    """Guarda o Conteúdo de um Fornecedor + código, registrando quem mudou e quando (ADR-0007).

    Sem mudança de valor, não há registro: o histórico lista só alterações. A exceção é a decisão
    explícita de manter o valor ("Manter 1" na sugestão de Conteúdo, decisão da usuária no ticket 08).
    """
    anterior = conteudo_guardado(conteudos_guardados(fornecedor.pk), codigo)
    if conteudo == anterior and not decisao_explicita:
        return
    AlteracaoDeConteudo.objects.create(
        fornecedor=fornecedor, codigo=codigo, gestor=gestor, data=hoje, valor_anterior=anterior, valor_novo=conteudo
    )


def definir_conteudo(gestor, fornecedor, codigo, conteudo, hoje=None):
    """Fora da Revisão. Muda o Preço unitário de todas as Ofertas do Fornecedor + código, inclusive as de
    Catálogos anteriores: o Conteúdo é por Fornecedor + código. `conteudo` vem como a gestora digitou.
    """
    conteudo = conteudo_digitado(conteudo)
    if not Oferta.objects.filter(catalogo__fornecedor=fornecedor, codigo=codigo).exists():
        raise ErroDeNegocio(f'O Fornecedor {fornecedor.nome} não tem Oferta com o código {codigo}.')
    guardar_conteudo(gestor, fornecedor, codigo, conteudo, hoje or timezone.localdate())


def conteudo_digitado(texto):
    """Conteúdo como a gestora digitou: inteiro, maior ou igual a 1 ("3" vale; "3,0", "0" e "-1" não)."""
    texto = texto.strip()
    if not texto.isdecimal() or int(texto) < 1:  # isdecimal: só o que int() lê ("³" não)
        raise ErroDeNegocio('O Conteúdo precisa ser um número inteiro maior ou igual a 1.')
    return int(texto)


def historico_do_conteudo(gestor, fornecedor, codigo):
    """Alterações do Conteúdo de um Fornecedor + código, da mais recente para a mais antiga."""
    return AlteracaoDeConteudo.objects.filter(fornecedor=fornecedor, codigo=codigo).order_by('-pk')


LIMITE_DE_RESULTADOS = 200


@dataclass
class ResultadoDaBusca:
    ofertas: list  # no máximo LIMITE_DE_RESULTADOS
    total: int  # quantas Ofertas a busca encontrou, inclusive as que ficaram de fora do limite


def buscar_ofertas(gestor, texto, fornecedor=None, so_vigentes=True):
    """Qualquer Gestor busca em todos os Catálogos do grupo (ADR-0007)."""
    texto = texto.strip()
    if not texto and fornecedor is None:
        raise ErroDeNegocio('Digite um código ou parte da descrição, ou escolha um Fornecedor.')
    ofertas = Oferta.objects.select_related('catalogo__fornecedor').filter(busca__contains=normalizar(texto))
    if fornecedor is not None:
        ofertas = ofertas.filter(catalogo__fornecedor=fornecedor)
    if so_vigentes:
        ofertas = ofertas.exclude(Exists(_que_vale_mais_que_esta()))
    ofertas = ofertas.order_by('catalogo__fornecedor__nome', 'codigo', '-catalogo__data', '-pk')
    achadas = list(ofertas[:LIMITE_DE_RESULTADOS])
    _carregar_conteudos_e_teto(achadas)
    return ResultadoDaBusca(ofertas=achadas, total=ofertas.count())


def _carregar_conteudos_e_teto(ofertas):
    """Uma consulta por Fornecedor (Conteúdo) e uma só para o Teto, em vez de uma por Oferta, para calcular
    o Preço unitário e o destaque de cada resultado."""
    teto = teto_atual()
    guardados = {}
    for oferta in ofertas:
        oferta._teto = teto
        fornecedor_id = oferta.catalogo.fornecedor_id
        if fornecedor_id not in guardados:
            guardados[fornecedor_id] = conteudos_guardados(fornecedor_id)
        oferta._conteudo = conteudo_guardado(guardados[fornecedor_id], oferta.codigo)


def _que_vale_mais_que_esta():
    """Ofertas do mesmo Fornecedor + código que ganham da Oferta de fora (OuterRef) como vigente.

    Ganha a de Catálogo mais recente; no mesmo dia, a de menor Preço unitário (GLOSSARY). O Conteúdo é o
    mesmo para o Fornecedor + código, então comparar preço impresso × (100 − desconto) ordena igual ao Preço
    unitário, sem gravá-lo. No empate de valor, vale o Catálogo confirmado por último.
    """
    de_fora = OuterRef('catalogo__data')
    valor = _valor_antes_do_conteudo('preco_impresso', 'catalogo__desconto')
    valor_de_fora = _valor_antes_do_conteudo(OuterRef('preco_impresso'), OuterRef('catalogo__desconto'))
    return Oferta.objects.annotate(valor_do_desempate=valor).filter(
        Q(catalogo__data__gt=de_fora)
        | Q(catalogo__data=de_fora, valor_do_desempate__lt=valor_de_fora)
        | Q(catalogo__data=de_fora, valor_do_desempate=valor_de_fora, catalogo__pk__gt=OuterRef('catalogo__pk')),
        catalogo__fornecedor=OuterRef('catalogo__fornecedor'),
        codigo=OuterRef('codigo'),
    )


def _valor_antes_do_conteudo(preco_impresso, desconto):
    preco = F(preco_impresso) if isinstance(preco_impresso, str) else preco_impresso
    percentual = F(desconto) if isinstance(desconto, str) else desconto
    return ExpressionWrapper(preco * (100 - Coalesce(percentual, 0)), output_field=DecimalField())


# Sem vírgula, um ponto seguido de exatamente 3 dígitos parece separador de milhar.
PONTO_DE_MILHAR = re.compile(r'\.\d{3}(?!\d)')


def preco_digitado(texto, nome='O preço'):
    """Preço como a gestora digitou: "9,90", "1.234,56" ou "12.5". Vazio devolve None (ausente).

    `nome` abre a mensagem de recusa ("O preço", "O Teto de compra").
    """
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
        raise ErroDeNegocio(f'{nome} precisa ser maior que zero.')
    return preco


def definir_teto(gestor, valor):
    """O Teto é um valor único do grupo: definir de novo substitui o anterior. `valor` vem como a gestora digitou."""
    teto = preco_digitado(valor, nome='O Teto de compra')
    if teto is None:
        raise ErroDeNegocio('O Teto de compra precisa ser maior que zero.')
    TetoDeCompra.objects.update_or_create(pk=1, defaults={'valor': teto})


def obter_teto(gestor):
    """O Teto de compra do grupo, ou None quando ainda não foi definido (então nada é destacado)."""
    return teto_atual()


def obter_oferta(gestor, oferta_id):
    """Qualquer Gestor consulta qualquer Oferta (ADR-0007). Para as telas de Conteúdo."""
    return Oferta.objects.select_related('catalogo__fornecedor').get(pk=oferta_id)


def obter_catalogo(gestor, catalogo_id):
    """Qualquer Gestor consulta qualquer Catálogo: a base de compras é do grupo (ADR-0007)."""
    return Catalogo.objects.get(pk=catalogo_id)


def listar_catalogos_do_fornecedor(gestor, fornecedor):
    # Mais recente primeiro; no mesmo dia, o último confirmado primeiro.
    return Catalogo.objects.filter(fornecedor=fornecedor).order_by('-data', '-pk')


def _fornecedor_com_o_mesmo_nome(nome):
    # Compara em Python: o iexact do SQLite não iguala maiúsculas acentuadas ("Ó" e "ó").
    procurado = nome.casefold()
    return next(
        (f for f in Fornecedor.objects.all() if f.nome.casefold() == procurado), None
    )
