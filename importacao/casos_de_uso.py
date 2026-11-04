"""Casos de uso do módulo Importação e Revisão. As telas e os testes entram por aqui."""

from django.db import transaction

from extracao.extrair import extrair_ofertas
from importacao.models import OfertaProposta, Revisao


def iniciar_importacao(gestor, fornecedor, arquivo):
    ofertas = extrair_ofertas(arquivo)
    with transaction.atomic():
        revisao = Revisao.objects.create(gestor=gestor, fornecedor=fornecedor)
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


def listar_revisoes_em_andamento(gestor):
    return Revisao.objects.filter(gestor=gestor)


def obter_revisao(gestor, revisao_id):
    return Revisao.objects.get(pk=revisao_id)
