"""Casos de uso do módulo Importação e Revisão. As telas e os testes entram por aqui."""

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


def confirmar_revisao(gestor, revisao_id):
    revisao = Revisao.objects.get(pk=revisao_id)
    # O Catálogo aponta para o mesmo arquivo guardado na Revisão: ele vira o arquivo de origem.
    # Transação única: se uma Oferta falhar, nem o Catálogo nem a marcação da Revisão ficam salvos.
    with transaction.atomic():
        catalogo = registrar_catalogo(
            gestor, revisao.fornecedor, revisao.iniciada_em, revisao.arquivo, revisao.ofertas_propostas()
        )
        revisao.catalogo = catalogo
        revisao.save()
    return catalogo


def listar_revisoes_em_andamento(gestor):
    return Revisao.objects.filter(gestor=gestor, catalogo__isnull=True)


def obter_revisao(gestor, revisao_id):
    # A Revisão em andamento é de quem iniciou a Importação (decisão da usuária no ticket 03).
    revisao = Revisao.objects.get(pk=revisao_id)
    if revisao.gestor_id != gestor.pk:
        raise AcessoNegado('Esta Revisão é de outro Gestor.')
    return revisao
