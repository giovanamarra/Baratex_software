# 39 — Foto da Oferta nos Catálogos em tabela (Excel e PDF)

Status: ready-for-agent
Type: task
Blocked by: 14, 23
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Foto; Modelo de dados › Foto)
ADRs: ADR-0011 (itens 1 e 3)
User stories: 116 (tabela em Excel e em PDF)

## O que entrega

Quando o arquivo do Catálogo é uma tabela com a foto de cada item (Excel com imagens nas linhas ou PDF em colunas com imagens), a foto vem junto com o código, a descrição, o preço e a Caixa.

## Critérios de aceite

- **Excel:** a imagem ancorada na linha da Oferta vira a foto dessa Oferta proposta.
- **PDF em tabela:** a imagem dentro da faixa vertical da linha vira a foto dessa Oferta proposta.
- Linha sem imagem → Oferta sem foto, sem marca e sem erro.
- Uma imagem fora de qualquer linha de Oferta (logo no cabeçalho, por exemplo) não vira foto de ninguém.
- As fotos são guardadas como no ticket 14 (reduzidas, pela impressão digital, sem duplicar) e aparecem na Revisão, na busca e na comparação.
- **Planilha de preços não dá foto** (ticket 36): o mesmo Excel com imagens, enviado como planilha de preços, cria Ofertas sem foto; a foto vem só do arquivo do Catálogo (ticket 38).

## Erros (mensagens em português)

- Nenhum erro novo: falta de imagem não é erro.

## O que o teste precisa

- O Catálogo fictício em tabela Excel do ticket 21, com imagens pequenas geradas no teste ancoradas em algumas linhas e uma no cabeçalho.
- O Catálogo fictício em tabela em PDF do ticket 23, com imagens dentro de algumas linhas.
- Nenhum fake da LLM.

## Fora deste ticket

- Foto recortada pela LLM (25, 26).
