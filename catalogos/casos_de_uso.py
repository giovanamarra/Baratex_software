"""Casos de uso do módulo Catálogos. As telas e os testes entram por aqui."""

from catalogos.models import Catalogo, Fornecedor, Oferta
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


def registrar_catalogo(gestor, fornecedor, data, arquivo, ofertas):
    """Cria o Catálogo e as suas Ofertas. Chamado pela Importação ao confirmar a Revisão."""
    catalogo = Catalogo.objects.create(gestor=gestor, fornecedor=fornecedor, data=data, arquivo=arquivo)
    Oferta.objects.bulk_create(
        Oferta(
            catalogo=catalogo,
            ordem=ordem,
            codigo=oferta.codigo,
            descricao=oferta.descricao,
            preco_impresso=oferta.preco_impresso,
            caixa=oferta.caixa,
            caminho=oferta.caminho,
        )
        for ordem, oferta in enumerate(ofertas)
    )
    return catalogo


def listar_catalogos_do_fornecedor(gestor, fornecedor):
    return Catalogo.objects.filter(fornecedor=fornecedor)


def _fornecedor_com_o_mesmo_nome(nome):
    # Compara em Python: o iexact do SQLite não iguala maiúsculas acentuadas ("Ó" e "ó").
    procurado = nome.casefold()
    return next(
        (f for f in Fornecedor.objects.all() if f.nome.casefold() == procurado), None
    )
