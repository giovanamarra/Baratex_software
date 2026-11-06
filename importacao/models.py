from django.conf import settings
from django.db import models

from catalogos.models import conteudo_guardado, conteudos_guardados, data_exibida, teto_atual
from catalogos.preco_unitario import acima_do_teto, calcular_preco_unitario
from importacao.marcas import fora_do_padrao, mediana_dos_precos, pecas_citadas, unidade_ambigua


class Revisao(models.Model):
    """Revisão em andamento: rascunho da Importação. Não é Catálogo até ser confirmada (spec, Revisão)."""

    gestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='revisoes')
    fornecedor = models.ForeignKey('catalogos.Fornecedor', on_delete=models.PROTECT)
    arquivo = models.FileField(upload_to='importacoes/%Y/%m/')
    iniciada_em = models.DateField()  # dia em que a Importação começou: o atalho "É de hoje" e o dia da Importação
    # Data do Catálogo informada pela gestora (ADR-0009). Só mês e ano fica guardado como o dia 1.
    data_do_catalogo = models.DateField(null=True)
    data_do_catalogo_so_mes_e_ano = models.BooleanField(default=False)
    # Condições do Catálogo: desconto em percentual (ex.: 3 = 3%), vazio = sem desconto. Guardado
    # como a gestora digitou, sem arredondar; só o Preço unitário é arredondado.
    desconto = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    # Preenchido ao confirmar. Sem Catálogo, a Revisão está em andamento.
    catalogo = models.OneToOneField(
        'catalogos.Catalogo', on_delete=models.PROTECT, null=True, related_name='revisao'
    )
    # Contagem da extração (história 33), guardada na Importação: o arquivo não é relido a cada tela.
    # Vazio quando o caminho não permite contar os preços.
    precos_no_arquivo = models.PositiveIntegerField(null=True)
    ofertas_extraidas = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Revisão'
        verbose_name_plural = 'Revisões'

    @property
    def data_do_catalogo_exibida(self):
        """Como a gestora informou: 15/10/2026 ou 10/2026. Vazio enquanto não informou."""
        return data_exibida(self.data_do_catalogo, self.data_do_catalogo_so_mes_e_ano)

    def ofertas_propostas(self):
        """Na ordem do arquivo, com as Ofertas de um código repetido juntas, onde o código aparece primeiro
        (ticket 32)."""
        ofertas = list(self.ofertas.order_by('ordem'))
        primeira_do_codigo = {}
        for posicao, oferta in enumerate(ofertas):
            primeira_do_codigo.setdefault(oferta.codigo, posicao)
        ofertas.sort(key=lambda oferta: primeira_do_codigo[oferta.codigo])  # estável: mantém a ordem do arquivo
        guardados = conteudos_guardados(self.fornecedor_id)  # uma consulta para a Revisão inteira
        mediana = mediana_dos_precos(oferta.preco_impresso for oferta in ofertas)
        teto = teto_atual()
        for oferta in ofertas:
            oferta._teto = teto
            oferta._conteudo_guardado = conteudo_guardado(guardados, oferta.codigo)
            oferta._ha_decisao_guardada = oferta.codigo in guardados
            oferta._mediana = mediana
        return ofertas

    @property
    def ofertas_que_faltam(self):
        """Quantos preços do arquivo não viraram Oferta (N − M); 0 quando não falta ou não dá para contar."""
        if self.precos_no_arquivo is None or self.ofertas_extraidas is None:
            return 0
        return max(self.precos_no_arquivo - self.ofertas_extraidas, 0)

    def mediana_dos_precos(self):
        return mediana_dos_precos(self.ofertas.values_list('preco_impresso', flat=True))


class OfertaProposta(models.Model):
    """Oferta extraída do arquivo, ainda em Revisão."""

    revisao = models.ForeignKey(Revisao, on_delete=models.CASCADE, related_name='ofertas')
    ordem = models.PositiveIntegerField()
    codigo = models.CharField(max_length=100)
    descricao = models.CharField(max_length=300)
    preco_impresso = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    caixa = models.PositiveIntegerField(null=True)
    caminho = models.CharField(max_length=30)
    # Conteúdo definido pela gestora nesta Revisão. Fica só aqui até a confirmação; vazio = não mexeu.
    conteudo_definido = models.PositiveIntegerField(null=True)
    # "Manter 1" na sugestão de Conteúdo: decisão explícita, guardada no histórico ao confirmar mesmo sem
    # mudar o valor (decisão da usuária, ticket 08). Diferente de conteudo_definido = 1, que o formulário
    # de Corrigir reenvia sem ser decisão.
    decidiu_manter_conteudo_1 = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Oferta proposta'
        verbose_name_plural = 'Ofertas propostas'

    @property
    def conteudo(self):
        """O definido nesta Revisão ou, sem ele, o guardado por Fornecedor + código (1 se nunca definido)."""
        if self.conteudo_definido is not None:
            return self.conteudo_definido
        if not hasattr(self, '_conteudo_guardado'):
            self._conteudo_guardado = conteudo_guardado(conteudos_guardados(self.revisao.fornecedor_id), self.codigo)
        return self._conteudo_guardado

    @property
    def preco_unitario(self):
        return calcular_preco_unitario(self.preco_impresso, self.revisao.desconto, self.conteudo)

    @property
    def acima_do_teto(self):
        # Derivado do Preço unitário na consulta, nunca gravado (ticket 10).
        if not hasattr(self, '_teto'):
            self._teto = teto_atual()
        return acima_do_teto(self.preco_unitario, self._teto)

    @property
    def marcas(self):
        """Marcas de conferência, em texto. Recalculadas a cada leitura: corrigir a Oferta muda as marcas."""
        if self.preco_impresso is None:
            return ['sem preço']
        if self.preco_impresso == 0:
            return ['preço zero']
        if not hasattr(self, '_mediana'):
            self._mediana = self.revisao.mediana_dos_precos()
        marcas = []
        if fora_do_padrao(self.preco_impresso, self._mediana):
            marcas.append('fora do padrão')
        if unidade_ambigua(self.descricao):
            marcas.append('unidade ambígua')
        return marcas

    @property
    def sugestao_de_conteudo(self):
        """Conteúdo sugerido quando a descrição cita peças. Só sugere: nunca muda o Conteúdo (história 42).

        Só aparece com o Conteúdo ainda em 1 e sem decisão guardada para o Fornecedor + código.
        """
        if not hasattr(self, '_ha_decisao_guardada'):
            self._ha_decisao_guardada = self.codigo in conteudos_guardados(self.revisao.fornecedor_id)
        if self.conteudo != 1 or self._ha_decisao_guardada or self.decidiu_manter_conteudo_1:
            return None
        citadas = pecas_citadas(self.descricao)
        return citadas[1] if citadas else None
