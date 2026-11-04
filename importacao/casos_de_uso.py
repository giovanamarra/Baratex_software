"""Casos de uso do módulo Importação e Revisão. As telas e os testes entram por aqui."""

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from catalogos.casos_de_uso import registrar_catalogo
from comparador.erros import AcessoNegado, ErroDeNegocio
from extracao.extrair import extrair_ofertas
from importacao.models import OfertaProposta, Revisao


def iniciar_importacao(gestor, fornecedor, arquivo, hoje=None):
    """`hoje` é injetável para os testes simularem dias diferentes; o padrão é o dia local."""
    if fornecedor is None:
        raise ErroDeNegocio('Escolha o Fornecedor do Catálogo.')
    if arquivo is None:
        raise ErroDeNegocio('Escolha o arquivo do Catálogo.')
    ofertas = extrair_ofertas(arquivo)
    arquivo.seek(0)
    with transaction.atomic():
        revisao = Revisao.objects.create(
            gestor=gestor,
            fornecedor=fornecedor,
            arquivo=arquivo,
            iniciada_em=hoje or timezone.localdate(),
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


def corrigir_oferta_proposta(gestor, oferta_id, codigo, descricao, preco_impresso, caixa):
    """Os valores chegam como a gestora digitou: preço "1.234,56" ou "9,90"; Caixa "24"; vazio = ausente."""
    oferta = _oferta_proposta_em_andamento(gestor, oferta_id)
    oferta.codigo = codigo.strip()
    oferta.descricao = descricao.strip()
    oferta.preco_impresso = _preco_digitado(preco_impresso)
    oferta.caixa = _caixa_digitada(caixa)
    oferta.save()


CAMINHO_MANUAL = 'manual'


def adicionar_oferta_proposta(gestor, revisao_id, codigo, descricao, preco_impresso, caixa):
    """Oferta digitada pela gestora, para um item que a extração não encontrou (história 35)."""
    revisao = _revisao_em_andamento(gestor, revisao_id)
    ultima = revisao.ofertas.order_by('-ordem').first()
    return OfertaProposta.objects.create(
        revisao=revisao,
        ordem=ultima.ordem + 1 if ultima else 0,
        codigo=codigo.strip(),
        descricao=descricao.strip(),
        preco_impresso=_preco_digitado(preco_impresso),
        caixa=_caixa_digitada(caixa),
        caminho=CAMINHO_MANUAL,
    )


def _preco_digitado(texto):
    texto = texto.strip()
    if not texto:
        return None
    if ',' in texto:  # formato brasileiro: ponto separa milhar, vírgula separa centavos
        texto = texto.replace('.', '').replace(',', '.')
    return Decimal(texto)


def _caixa_digitada(texto):
    texto = texto.strip()
    return int(texto) if texto else None


def _desconto_valido(texto):
    try:
        desconto = Decimal(texto.strip().replace(',', '.'))
    except InvalidOperation:
        desconto = None
    if desconto is None or not desconto.is_finite() or not 0 <= desconto < 100:
        raise ErroDeNegocio('O desconto precisa ser de 0% até menos de 100%.')
    return desconto


def confirmar_revisao(gestor, revisao_id):
    revisao = _revisao_em_andamento(gestor, revisao_id)
    # O Catálogo aponta para o mesmo arquivo guardado na Revisão: ele vira o arquivo de origem.
    # Transação única: se uma Oferta falhar, nem o Catálogo nem a marcação da Revisão ficam salvos.
    with transaction.atomic():
        catalogo = registrar_catalogo(
            gestor,
            revisao.fornecedor,
            revisao.iniciada_em,
            revisao.arquivo,
            revisao.desconto,
            revisao.ofertas_propostas(),
        )
        revisao.catalogo = catalogo
        revisao.save()
    return catalogo


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
