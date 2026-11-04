"""Conferência local do leitor do Layout A com os Catálogos reais. Não roda na suíte de testes.

Uso (da raiz do projeto):

    .venv/bin/python ferramentas/conferir_catalogos_reais.py catalogos-exemplo

Imprime só números por arquivo, nunca código, descrição, preço ou nome de marca: a saída pode ser
mostrada sem expor dados reais. Os arquivos são numerados pela ordem alfabética do nome na pasta.
"""

import sys
import time
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extracao.grade_de_cartoes import e_layout_a, ler_layout_a  # noqa: E402

ASSINATURA_DE_PDF = b'%PDF'
ROTULO_DE_CONTAGEM = 'Disponibilidade:'


def conferir(arquivo):
    """Números de um arquivo: reconhecido, cartões, Ofertas, sem preço, sem Caixa e tempo."""
    if arquivo.read_bytes()[: len(ASSINATURA_DE_PDF)] != ASSINATURA_DE_PDF:
        return {'pdf': False}
    inicio = time.perf_counter()
    with pdfplumber.open(arquivo) as pdf:
        reconhecido = e_layout_a(pdf)
        numeros = {'pdf': True, 'reconhecido': reconhecido}
        if reconhecido:
            # Contados por outro rótulo do cartão, não pela âncora do leitor ("Código:"), para a
            # comparação cartões × Ofertas não bater por construção.
            cartoes = sum(
                1 for pagina in pdf.pages for palavra in pagina.extract_words()
                if palavra['text'].startswith(ROTULO_DE_CONTAGEM)
            )
            ofertas = ler_layout_a(pdf)
            numeros.update(
                cartoes=cartoes,
                ofertas=len(ofertas),
                sem_preco=sum(1 for oferta in ofertas if oferta.preco_impresso is None),
                sem_caixa=sum(1 for oferta in ofertas if oferta.caixa is None),
            )
    numeros['segundos'] = time.perf_counter() - inicio
    return numeros


def linha(indice, numeros):
    rotulo = f'arquivo {indice:02d}'
    if not numeros['pdf']:
        return f'{rotulo}  não é PDF'
    if not numeros['reconhecido']:
        return f'{rotulo}  reconhecido: não  tempo: {numeros["segundos"]:.2f} s'
    return (
        f'{rotulo}  reconhecido: sim  cartões: {numeros["cartoes"]:4d}  Ofertas: {numeros["ofertas"]:4d}  '
        f'sem preço: {numeros["sem_preco"]}  sem Caixa: {numeros["sem_caixa"]}  tempo: {numeros["segundos"]:.2f} s'
    )


def main(pasta):
    arquivos = sorted(caminho for caminho in Path(pasta).iterdir() if caminho.is_file())
    total = dict.fromkeys(('reconhecidos', 'cartoes', 'ofertas', 'sem_preco', 'sem_caixa', 'segundos'), 0)
    for indice, arquivo in enumerate(arquivos, start=1):
        numeros = conferir(arquivo)
        print(linha(indice, numeros))
        total['segundos'] += numeros.get('segundos', 0)
        if numeros.get('reconhecido'):
            total['reconhecidos'] += 1
            for chave in ('cartoes', 'ofertas', 'sem_preco', 'sem_caixa'):
                total[chave] += numeros[chave]
    print(
        f'total  arquivos: {len(arquivos)}  reconhecidos: {total["reconhecidos"]}  cartões: {total["cartoes"]}  '
        f'Ofertas: {total["ofertas"]}  sem preço: {total["sem_preco"]}  sem Caixa: {total["sem_caixa"]}  '
        f'tempo: {total["segundos"]:.1f} s'
    )


if __name__ == '__main__':
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit('Uso: .venv/bin/python ferramentas/conferir_catalogos_reais.py <pasta dos Catálogos>')
    main(sys.argv[1])
