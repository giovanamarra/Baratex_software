from django.conf import settings
from django.db import models

from catalogos.preco_unitario import acima_do_teto, calcular_preco_unitario


class Fornecedor(models.Model):
    """Empresa que vende produtos ao grupo (GLOSSARY). Pertence ao grupo (ADR-0007)."""

    nome = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.nome


class Catalogo(models.Model):
    """Conjunto de preços de um Fornecedor, datado pelo dia da Importação. Nunca é sobrescrito."""

    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='catalogos')
    gestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='catalogos_importados')
    arquivo = models.FileField(upload_to='importacoes/%Y/%m/')
    data = models.DateField()  # dia em que a Importação começou
    # Condições do Catálogo: desconto percentual (ex.: 3 = 3%); vazio = sem desconto.
    desconto = models.DecimalField(max_digits=7, decimal_places=4, null=True)

    class Meta:
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogos'

    def ofertas(self):
        ofertas = list(self.ofertas_do_catalogo.order_by('ordem'))
        guardados = conteudos_guardados(self.fornecedor_id)  # uma consulta para o Catálogo inteiro
        teto = teto_atual()  # idem para o destaque do Teto
        for oferta in ofertas:
            oferta._conteudo = conteudo_guardado(guardados, oferta.codigo)
            oferta._teto = teto
        return ofertas


class Oferta(models.Model):
    """Um item de um Catálogo: algo que o Fornecedor propõe vender, com o preço daquele Catálogo."""

    catalogo = models.ForeignKey(Catalogo, on_delete=models.PROTECT, related_name='ofertas_do_catalogo')
    ordem = models.PositiveIntegerField()
    codigo = models.CharField(max_length=100)
    descricao = models.CharField(max_length=300)
    preco_impresso = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    caixa = models.PositiveIntegerField(null=True)
    caminho = models.CharField(max_length=30)
    # Código e descrição sem acento e em minúsculas, preenchidos ao confirmar a Revisão (ver catalogos.busca).
    busca = models.TextField(default='', editable=False)

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        # A vigência compara cada Oferta com as de mesmo código em outros Catálogos (ver buscar_ofertas).
        indexes = [models.Index(fields=['codigo'], name='oferta_codigo_idx')]
        constraints = [
            # Preço impresso pode faltar (é mascarado em alguns Catálogos), mas nunca é negativo.
            models.CheckConstraint(
                condition=models.Q(preco_impresso__gte=0) | models.Q(preco_impresso__isnull=True),
                name='oferta_preco_impresso_nao_negativo',
            ),
        ]

    @property
    def conteudo(self):
        # Guardado por Fornecedor + código, não por Oferta: vale para todos os Catálogos do Fornecedor.
        if not hasattr(self, '_conteudo'):
            self._conteudo = conteudo_guardado(conteudos_guardados(self.catalogo.fornecedor_id), self.codigo)
        return self._conteudo

    @property
    def preco_unitario(self):
        return calcular_preco_unitario(self.preco_impresso, self.catalogo.desconto, self.conteudo)

    @property
    def acima_do_teto(self):
        # Derivado na consulta, nunca gravado: mudar o Teto muda o destaque sem nenhum outro passo.
        if not hasattr(self, '_teto'):
            self._teto = teto_atual()
        return acima_do_teto(self.preco_unitario, self._teto)


class AlteracaoDeConteudo(models.Model):
    """Registro de cada mudança do Conteúdo de um Fornecedor + código (ADR-0007, auditoria).

    O Conteúdo atual é o valor novo da alteração mais recente; sem alteração, vale 1 (história 42).
    """

    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='alteracoes_de_conteudo')
    codigo = models.CharField(max_length=100)
    gestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    data = models.DateField()
    valor_anterior = models.PositiveIntegerField()
    valor_novo = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Alteração de Conteúdo'
        verbose_name_plural = 'Alterações de Conteúdo'


class TetoDeCompra(models.Model):
    """Maior Preço unitário que ainda permite revender com lucro. Um único valor para o grupo (ADR-0007):
    há no máximo uma linha, e definir de novo substitui o valor."""

    valor = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Teto de compra'
        verbose_name_plural = 'Teto de compra'


def teto_atual():
    """O Teto de compra do grupo, ou None quando ainda não foi definido."""
    return TetoDeCompra.objects.values_list('valor', flat=True).first()


CONTEUDO_PADRAO = 1


def conteudos_guardados(fornecedor_id):
    """Conteúdo atual de cada código do Fornecedor que já teve o Conteúdo definido."""
    alteracoes = AlteracaoDeConteudo.objects.filter(fornecedor_id=fornecedor_id).order_by('pk')
    return dict(alteracoes.values_list('codigo', 'valor_novo'))  # a mais recente vence


def conteudo_guardado(guardados, codigo):
    return guardados.get(codigo, CONTEUDO_PADRAO)
