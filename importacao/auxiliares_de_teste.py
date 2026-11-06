"""Auxiliares dos testes de Importação, reutilizados pelos próximos tickets."""

import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase, override_settings

from importacao.casos_de_uso import corrigir_oferta_proposta, informar_data_do_catalogo, obter_revisao


class ArquivosEnviadosTemporarios:
    """Guarda os arquivos enviados numa pasta temporária, apagada no fim. Nunca em media/."""

    @classmethod
    def setUpClass(cls):
        cls._pasta_de_arquivos = tempfile.mkdtemp()
        cls._media_temporaria = override_settings(MEDIA_ROOT=cls._pasta_de_arquivos)
        cls._media_temporaria.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_temporaria.disable()
        shutil.rmtree(cls._pasta_de_arquivos, ignore_errors=True)


class TesteComArquivosEnviados(ArquivosEnviadosTemporarios, TestCase):
    pass


class TesteTransacionalComArquivosEnviados(ArquivosEnviadosTemporarios, TransactionTestCase):
    """Grava de verdade no banco de teste: para provar o que uma transação desfaz ou não."""


def arquivo_enviado(conteudo, nome='catalogo.pdf'):
    return SimpleUploadedFile(nome, conteudo)


def corrigir(gestor, oferta, **mudancas):
    """Corrige na Revisão só os campos pedidos, repetindo os outros como o formulário de Corrigir."""
    valores = {
        'codigo': oferta.codigo,
        'descricao': oferta.descricao,
        'preco_impresso': '' if oferta.preco_impresso is None else str(oferta.preco_impresso),
        'caixa': '' if oferta.caixa is None else str(oferta.caixa),
        'conteudo': str(oferta.conteudo),
    }
    corrigir_oferta_proposta(gestor, oferta.pk, **{**valores, **mudancas})


def resumo(oferta):
    """Os campos que a Revisão e o Catálogo guardam de uma Oferta, para comparar em testes."""
    return (oferta.codigo, oferta.descricao, oferta.preco_impresso, oferta.caixa, oferta.caminho)


def informar_data_de_hoje(gestor, revisao_id):
    """Como o atalho "É de hoje" da Revisão: a data do Catálogo é o dia em que a Importação começou.

    Para os testes que não tratam da data do Catálogo (desde o ticket 31, confirmar exige a data).
    """
    iniciada_em = obter_revisao(gestor, revisao_id).iniciada_em
    informar_data_do_catalogo(gestor, revisao_id, f'{iniciada_em:%d/%m/%Y}', hoje=iniciada_em)
