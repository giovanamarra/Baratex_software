"""Casos de uso do módulo Catálogos. As telas e os testes entram por aqui."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import DecimalField, Exists, ExpressionWrapper, F, Func, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from catalogos.busca import normalizar, texto_de_busca
from catalogos.models import (
    CONTEUDO_PADRAO,
    AlteracaoDeConteudo,
    Catalogo,
    CorrecaoDaDataDoCatalogo,
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


def registrar_catalogo(gestor, fornecedor, data, data_so_mes_e_ano, importado_em, arquivo, desconto, ofertas):
    """Cria o Catálogo e as suas Ofertas. Chamado pela Importação ao confirmar a Revisão."""
    catalogo = Catalogo.objects.create(
        gestor=gestor,
        fornecedor=fornecedor,
        data=data,
        data_so_mes_e_ano=data_so_mes_e_ano,
        importado_em=importado_em,
        arquivo=arquivo,
        desconto=desconto,
    )
    Oferta.objects.bulk_create(
        Oferta(
            catalogo=catalogo,
            # A posição no arquivo (ordem de leitura; a adicionada à mão fica depois). Desempata o código
            # repetido no Catálogo (ticket 32), então vem da Oferta proposta, não da ordem em que chegam aqui.
            ordem=oferta.ordem,
            codigo=oferta.codigo,
            descricao=oferta.descricao,
            preco_impresso=oferta.preco_impresso,
            caixa=oferta.caixa,
            caminho=oferta.caminho,
            busca=texto_de_busca(oferta.codigo, oferta.descricao),
        )
        for oferta in ofertas
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
    """Ofertas do mesmo Fornecedor + código que ganham da Oferta de fora (OuterRef) como vigente (ADR-0009).

    Ganha a do Catálogo de data do Catálogo mais recente, mesmo que o preço tenha subido (só mês e ano está
    guardado como o dia 1). Na mesma data, a do Catálogo confirmado por último: o Catálogo é criado na
    confirmação, então o maior pk é o último confirmado. Calculado na consulta, nunca gravado.

    O código repetido no mesmo Catálogo (ticket 32): ganha a de menor Preço unitário e, com Preço unitário
    igual, a que aparece primeiro no arquivo (menor ordem).
    """
    data_de_fora = OuterRef('catalogo__data')
    # As duas Ofertas são do mesmo Catálogo e do mesmo Fornecedor + código: o desconto e o Conteúdo são os
    # mesmos, e os desta servem para as duas.
    desconto = Coalesce(F('catalogo__desconto'), 0, output_field=DecimalField())
    conteudo = Coalesce(
        Subquery(
            AlteracaoDeConteudo.objects.filter(fornecedor=OuterRef('catalogo__fornecedor'), codigo=OuterRef('codigo'))
            .order_by('-pk')
            .values('valor_novo')[:1]
        ),
        CONTEUDO_PADRAO,
    )
    return (
        Oferta.objects.annotate(
            preco_unitario_em_centavos=_preco_unitario_em_centavos(F('preco_impresso'), desconto, conteudo),
            preco_unitario_de_fora_em_centavos=_preco_unitario_em_centavos(
                OuterRef('preco_impresso'), desconto, conteudo
            ),
        )
        .filter(
            Q(catalogo__data__gt=data_de_fora)
            | Q(catalogo__data=data_de_fora, catalogo__pk__gt=OuterRef('catalogo__pk'))
            | Q(catalogo=OuterRef('catalogo'), preco_unitario_em_centavos__lt=F('preco_unitario_de_fora_em_centavos'))
            | Q(
                catalogo=OuterRef('catalogo'),
                preco_unitario_em_centavos=F('preco_unitario_de_fora_em_centavos'),
                ordem__lt=OuterRef('ordem'),
            ),
            catalogo__fornecedor=OuterRef('catalogo__fornecedor'),
            codigo=OuterRef('codigo'),
        )
    )


def _preco_unitario_em_centavos(preco_impresso, desconto, conteudo):
    """O Preço unitário de catalogos.preco_unitario, em centavos, calculado no SQLite só com inteiros (o SQLite
    não tem decimal, e o float erraria o meio centavo).

    Com o preço em centavos (P), o desconto em décimos de milésimo de ponto percentual (D: 100% = 1.000.000, as
    4 casas do campo) e o Conteúdo (C): P × (1 − D/1.000.000) ÷ C, com meio centavo para cima, é
    (2 × P × (1.000.000 − D) + 1.000.000 × C) ÷ (2.000.000 × C) na divisão inteira. Com o maior preço (cerca de
    10¹² centavos), o produto fica perto de 2 × 10¹⁸, abaixo do limite do inteiro do SQLite (9,2 × 10¹⁸).
    """
    centavos = _inteiro_do_sqlite(preco_impresso, 100)
    desconto = _inteiro_do_sqlite(desconto, 10_000)
    return ExpressionWrapper(
        (2 * centavos * (1_000_000 - desconto) + 1_000_000 * conteudo) / (2_000_000 * conteudo),
        output_field=IntegerField(),
    )


def _inteiro_do_sqlite(decimal, escala):
    """O decimal × escala como inteiro do SQLite (o decimal fica guardado como número de ponto flutuante)."""
    return Func(decimal, template=f'CAST(ROUND(%(expressions)s * {escala}) AS INTEGER)', output_field=IntegerField())


# O maior valor que cabe nas colunas de preço (12 dígitos, 2 casas); acima disso o banco recusa a gravação.
MAIOR_PRECO = Decimal('9999999999.99')

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
    if preco > MAIOR_PRECO:
        raise ErroDeNegocio(f'{nome} é grande demais. Confira se digitou o valor certo.')
    return preco


# dia/mês/ano ou mês/ano; o ano com 4 dígitos ou 2 (20xx).
DATA_DO_CATALOGO = re.compile(r'(?:(?P<dia>\d{1,2})/)?(?P<mes>\d{1,2})/(?P<ano>\d{4}|\d{2})')
FORMATO_DA_DATA_DO_CATALOGO = (
    'Informe a data do Catálogo como dia/mês/ano ou mês/ano, por exemplo 15/10/2026 ou 10/2026.'
)


def data_do_catalogo_digitada(texto, hoje):
    """Data do Catálogo como a gestora digitou (ADR-0009): 15/10/2026, 10/2026 ou 15/10/26 (ano com 2 dígitos =
    20xx). Devolve (data, só mês e ano); só mês e ano fica como o dia 1, que é como conta para a vigência."""
    formato = DATA_DO_CATALOGO.fullmatch(texto.strip())
    if not formato:
        raise ErroDeNegocio(FORMATO_DA_DATA_DO_CATALOGO)
    so_mes_e_ano = formato['dia'] is None
    dia, mes, ano = 1 if so_mes_e_ano else int(formato['dia']), int(formato['mes']), int(formato['ano'])
    if ano < 100:
        ano += 2000
    if ano < 2000:  # erro de digitação: um preço desses ficaria vigente por anos (102)
        raise ErroDeNegocio('Confira o ano da data do Catálogo.')
    try:
        data = date(ano, mes, dia)
    except ValueError:  # 31/02/2026, 13/2026
        raise ErroDeNegocio(FORMATO_DA_DATA_DO_CATALOGO)
    if data > hoje:
        raise ErroDeNegocio('A data do Catálogo não pode ser depois de hoje.')
    return data, so_mes_e_ano


def corrigir_data_do_catalogo(gestor, catalogo_id, texto, hoje=None):
    """Qualquer Gestor corrige a data de um Catálogo confirmado (ADR-0009, item 6): é o único dado do Catálogo que
    muda depois da confirmação. `texto` como a gestora digitou; `hoje` é injetável nos testes."""
    hoje = hoje or timezone.localdate()
    catalogo = _catalogo_existente(catalogo_id)
    anterior = catalogo.data, catalogo.data_so_mes_e_ano
    nova = data_do_catalogo_digitada(texto, hoje)
    if nova == anterior:  # a mesma data, com a mesma precisão, não é correção: nada muda nem é registrado
        return
    catalogo.data, catalogo.data_so_mes_e_ano = nova
    catalogo.save(update_fields=['data', 'data_so_mes_e_ano'])
    CorrecaoDaDataDoCatalogo.objects.create(
        catalogo=catalogo,
        gestor=gestor,
        dia=hoje,
        data_anterior=anterior[0],
        data_anterior_so_mes_e_ano=anterior[1],
        data_nova=catalogo.data,
        data_nova_so_mes_e_ano=catalogo.data_so_mes_e_ano,
    )


@dataclass
class ImpactoDaNovaData:
    deixam_de_ser_vigentes: int
    passam_a_ser_vigentes: int

    @property
    def mensagem(self):
        if self.passam_a_ser_vigentes:
            return f'Com a nova data, {self.passam_a_ser_vigentes} Ofertas deste Catálogo passam a ser vigentes.'
        if self.deixam_de_ser_vigentes:
            return f'Com a nova data, {self.deixam_de_ser_vigentes} Ofertas deste Catálogo deixam de ser vigentes.'
        return 'Com a nova data, nenhuma Oferta deste Catálogo muda de vigência.'


def ver_impacto_da_nova_data(gestor, catalogo_id, texto, hoje=None):
    """Quantas Ofertas deste Catálogo mudam de vigência com a nova data, antes de salvar (história 104). É só
    aviso: corrigir_data_do_catalogo recalcula ao salvar."""
    catalogo = _catalogo_existente(catalogo_id)
    data, so_mes_e_ano = data_do_catalogo_digitada(texto, hoje or timezone.localdate())
    antes = _vigentes_do_catalogo(catalogo)
    # A mesma regra de vigência da busca, com a data nova gravada só dentro de uma transação desfeita em seguida:
    # nenhuma segunda implementação da regra (ADR-0009).
    with transaction.atomic():
        Catalogo.objects.filter(pk=catalogo.pk).update(data=data, data_so_mes_e_ano=so_mes_e_ano)
        depois = _vigentes_do_catalogo(catalogo)
        transaction.set_rollback(True)
    return ImpactoDaNovaData(deixam_de_ser_vigentes=len(antes - depois), passam_a_ser_vigentes=len(depois - antes))


def _vigentes_do_catalogo(catalogo):
    vigentes = Oferta.objects.filter(catalogo=catalogo).exclude(Exists(_que_vale_mais_que_esta()))
    return set(vigentes.values_list('pk', flat=True))


def _catalogo_existente(catalogo_id):
    catalogo = Catalogo.objects.filter(pk=catalogo_id).first()
    if catalogo is None:
        raise ErroDeNegocio('Catálogo não encontrado.')
    return catalogo


def correcoes_da_data(gestor, catalogo_id):
    """As correções da data de um Catálogo, da mais recente para a mais antiga (para a página do Catálogo)."""
    return CorrecaoDaDataDoCatalogo.objects.filter(catalogo_id=catalogo_id).order_by('-pk')


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
    # Pela data do Catálogo, da mais recente para a mais antiga; na mesma data, o confirmado por último primeiro (58).
    return Catalogo.objects.filter(fornecedor=fornecedor).order_by('-data', '-pk')


def _fornecedor_com_o_mesmo_nome(nome):
    # Compara em Python: o iexact do SQLite não iguala maiúsculas acentuadas ("Ó" e "ó").
    procurado = nome.casefold()
    return next(
        (f for f in Fornecedor.objects.all() if f.nome.casefold() == procurado), None
    )
