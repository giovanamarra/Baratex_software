from django.conf import settings
from django.db import models

from catalogos.models import conteudo_guardado, conteudos_guardados
from catalogos.preco_unitario import calcular_preco_unitario


class Revisao(models.Model):
    """Revisão em andamento: rascunho da Importação. Não é Catálogo até ser confirmada (spec, Revisão)."""

    gestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='revisoes')
    fornecedor = models.ForeignKey('catalogos.Fornecedor', on_delete=models.PROTECT)
    arquivo = models.FileField(upload_to='importacoes/%Y/%m/')
    iniciada_em = models.DateField()  # vira a data do Catálogo (história 15)
    # Condições do Catálogo: desconto em percentual (ex.: 3 = 3%), vazio = sem desconto. Guardado
    # como a gestora digitou, sem arredondar; só o Preço unitário é arredondado.
    desconto = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    # Preenchido ao confirmar. Sem Catálogo, a Revisão está em andamento.
    catalogo = models.OneToOneField(
        'catalogos.Catalogo', on_delete=models.PROTECT, null=True, related_name='revisao'
    )

    class Meta:
        verbose_name = 'Revisão'
        verbose_name_plural = 'Revisões'

    def ofertas_propostas(self):
        ofertas = list(self.ofertas.order_by('ordem'))
        guardados = conteudos_guardados(self.fornecedor_id)  # uma consulta para a Revisão inteira
        for oferta in ofertas:
            oferta._conteudo_guardado = conteudo_guardado(guardados, oferta.codigo)
        return ofertas


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
    def marcas(self):
        """Marcas de conferência, em texto (o ticket 08 acrescenta as outras)."""
        if self.preco_impresso is None:
            return ['sem preço']
        if self.preco_impresso == 0:
            return ['preço zero']
        return []
