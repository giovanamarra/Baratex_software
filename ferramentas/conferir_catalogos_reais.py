"""Conferência local do leitor do Layout A com os Catálogos reais. Não roda na suíte de testes.

Uso (da raiz do projeto):

    .venv/bin/python ferramentas/conferir_catalogos_reais.py catalogos-exemplo

Imprime só números por arquivo, nunca código, descrição, preço ou nome de marca: a saída pode ser
mostrada sem expor dados reais. Os arquivos são numerados pela ordem alfabética do nome na pasta.

Três tabelas: a leitura (reconhecido, cartões, Ofertas, sem preço, sem Caixa, tempo), a calibração
das marcas de conferência do ticket 08 (fora do padrão, Unidade de venda ambígua, sugestão de
Conteúdo por padrão e preços no arquivo × Ofertas extraídas) e o código repetido no mesmo Catálogo
do ticket 32 (códigos repetidos, Ofertas nesses códigos e quantos deles estão em páginas diferentes).
"""

import sys
import time
from collections import Counter
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# As mesmas regras da aplicação (ticket 08): o script mede o código de verdade, não uma cópia.
from extracao.grade_de_cartoes import e_layout_a, ler_layout_a  # noqa: E402
from importacao.marcas import (  # noqa: E402
    PADROES_DE_PECAS,
    fora_do_padrao as preco_fora_do_padrao,
    mediana_dos_precos,
    pecas_citadas,
    unidade_ambigua as ambigua,
)

ASSINATURA_DE_PDF = b'%PDF'
ROTULO_DE_CONTAGEM = 'Disponibilidade:'


def fora_do_padrao(ofertas):
    mediana = mediana_dos_precos(oferta.preco_impresso for oferta in ofertas)
    return sum(1 for oferta in ofertas if preco_fora_do_padrao(oferta.preco_impresso, mediana))


def padrao_de_pecas(descricao):
    """O nome do padrão que cita peças (para a contagem por padrão), ou None."""
    citadas = pecas_citadas(descricao)
    return citadas[0] if citadas else None


def codigos_repetidos(ofertas):
    """Códigos que aparecem mais de uma vez no arquivo, comparados como a Revisão compara (ticket 32)."""
    paginas = {}
    for oferta in ofertas:
        paginas.setdefault(oferta.codigo, []).append(oferta.pagina)
    repetidos = [lista for lista in paginas.values() if len(lista) > 1]
    return {
        'codigos_repetidos': len(repetidos),
        'ofertas_repetidas': sum(len(lista) for lista in repetidos),
        'repetidos_em_paginas_diferentes': sum(1 for lista in repetidos if len(set(lista)) > 1),
    }


def precos_no_arquivo(pdf):
    """Ocorrências de "R$" no texto do PDF, e quantas delas são preço mascarado ("R$***,**")."""
    textos = [p['text'] for pagina in pdf.pages for p in pagina.extract_words() if p['text'].startswith('R$')]
    return len(textos), sum(1 for texto in textos if '*' in texto)


def conferir(arquivo):
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
            precos, mascarados = precos_no_arquivo(pdf)
            numeros.update(
                fora_do_padrao=fora_do_padrao(ofertas),
                ambiguas=sum(1 for oferta in ofertas if ambigua(oferta.descricao)),
                sugestoes=Counter(filter(None, (padrao_de_pecas(oferta.descricao) for oferta in ofertas))),
                precos_no_arquivo=precos,
                mascarados=mascarados,
                **codigos_repetidos(ofertas),
            )
            return numeros
    numeros['segundos'] = time.perf_counter() - inicio
    return numeros


def linha_de_leitura(indice, numeros):
    rotulo = f'arquivo {indice:02d}'
    if not numeros['pdf']:
        return f'{rotulo}  não é PDF'
    if not numeros['reconhecido']:
        return f'{rotulo}  reconhecido: não  tempo: {numeros["segundos"]:.2f} s'
    return (
        f'{rotulo}  reconhecido: sim  cartões: {numeros["cartoes"]:4d}  Ofertas: {numeros["ofertas"]:4d}  '
        f'sem preço: {numeros["sem_preco"]}  sem Caixa: {numeros["sem_caixa"]}  tempo: {numeros["segundos"]:.2f} s'
    )


def percentual(parte, todo):
    return f'{parte} ({100 * parte / todo:.1f}%)' if todo else str(parte)


def linha_de_calibracao(rotulo, numeros):
    sugestoes = numeros['sugestoes']
    por_padrao = ', '.join(f'{nome}: {sugestoes[nome]}' for nome in PADROES_DE_PECAS if sugestoes[nome])
    return (
        f'{rotulo}  Ofertas: {numeros["ofertas"]:4d}  fora do padrão: {percentual(numeros["fora_do_padrao"], numeros["ofertas"])}  '
        f'ambígua: {percentual(numeros["ambiguas"], numeros["ofertas"])}  '
        f'sugestão: {percentual(sum(sugestoes.values()), numeros["ofertas"])}{f" [{por_padrao}]" if por_padrao else ""}  '
        f'preços no arquivo: {numeros["precos_no_arquivo"]} (mascarados: {numeros["mascarados"]})'
    )


def main(pasta):
    arquivos = sorted(caminho for caminho in Path(pasta).iterdir() if caminho.is_file())
    resultados = [(indice, conferir(arquivo)) for indice, arquivo in enumerate(arquivos, start=1)]
    lidos = [(indice, numeros) for indice, numeros in resultados if numeros.get('reconhecido')]

    print('Leitura')
    for indice, numeros in resultados:
        print(linha_de_leitura(indice, numeros))
    total = {chave: sum(n[chave] for _, n in lidos) for chave in ('cartoes', 'ofertas', 'sem_preco', 'sem_caixa')}
    print(
        f'total  arquivos: {len(arquivos)}  reconhecidos: {len(lidos)}  cartões: {total["cartoes"]}  '
        f'Ofertas: {total["ofertas"]}  sem preço: {total["sem_preco"]}  sem Caixa: {total["sem_caixa"]}  '
        f'tempo: {sum(n.get("segundos", 0) for _, n in resultados):.1f} s'
    )

    print('\nCalibração das marcas (ticket 08)')
    for indice, numeros in lidos:
        print(linha_de_calibracao(f'arquivo {indice:02d}', numeros))
    soma = {chave: sum(n[chave] for _, n in lidos) for chave in
            ('ofertas', 'fora_do_padrao', 'ambiguas', 'precos_no_arquivo', 'mascarados')}
    soma['sugestoes'] = sum((n['sugestoes'] for _, n in lidos), Counter())
    print(linha_de_calibracao('total     ', soma))

    print('\nCódigo repetido no mesmo Catálogo (ticket 32)')
    chaves = ('codigos_repetidos', 'ofertas_repetidas', 'repetidos_em_paginas_diferentes')
    for rotulo, numeros in [*((f'arquivo {i:02d}', n) for i, n in lidos), ('total     ', {c: sum(n[c] for _, n in lidos) for c in chaves})]:
        print(
            f'{rotulo}  códigos repetidos: {numeros["codigos_repetidos"]}  Ofertas nesses códigos: '
            f'{numeros["ofertas_repetidas"]}  em páginas diferentes: {numeros["repetidos_em_paginas_diferentes"]}'
        )


if __name__ == '__main__':
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit('Uso: .venv/bin/python ferramentas/conferir_catalogos_reais.py <pasta dos Catálogos>')
    main(sys.argv[1])
