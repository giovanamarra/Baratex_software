# 08 — Marcas de conferência e contagem de preços na Revisão

Status: ready-for-agent
Type: task
Blocked by: 06, 07
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › marcas de conferência; Further Notes › heurísticas)
ADRs: ADR-0006 (marcas e contagem), ADR-0005 (Conteúdo padrão 1)
User stories: 30 (fora do padrão), 32, 33, 43

## O que entrega

A Revisão aponta o que a gestora deve olhar com atenção: preço muito fora do padrão do próprio Catálogo, Unidade de venda ambígua e descrição que cita peças. Ela também mostra quantos preços havia no arquivo e quantas Ofertas foram extraídas.

O spec delega a este ticket a definição das heurísticas, com exemplos fictícios e de forma fácil de explicar. As regras abaixo são a proposta e podem ser ajustadas antes da sessão de TDD.

## Critérios de aceite

- **Preço fora do padrão** (30): quando o Catálogo tem pelo menos 5 Ofertas com preço, fica marcada a Oferta cujo preço impresso é mais de 5 vezes a mediana dos preços do Catálogo, ou menos de 1/5 dela.
  - Exemplo: preços 9, 10, 10, 11, 12 e 100 → só a de 100 é marcada.
  - Com só 3 Ofertas com preço, nada é marcado como fora do padrão.
- **Unidade de venda ambígua** (32): fica marcada a Oferta cuja descrição tem, como palavra inteira, KIT, JOGO, CONJUNTO, SET ou PAR, ignorando maiúsculas e acentos.
- **Sugestão de Conteúdo** (43): quando a descrição cita uma quantidade de peças ("C/3", "COM 3 PEÇAS", "3 PÇS", "3 PCS", "3 UNID"), a Revisão sugere Conteúdo 3. A sugestão só aparece se o Conteúdo ainda for 1 e não houver decisão guardada para esse Fornecedor + código. Aceitar a sugestão é definir o Conteúdo (ticket 07). O sistema nunca muda o Conteúdo sozinho (42).
- **Contagem** (33): no caminho de grade de cartões, a Revisão mostra "Preços no arquivo: N · Ofertas extraídas: M", contando as ocorrências de preço no texto do PDF. Quando M < N, a diferença fica destacada.
- As marcas são recalculadas depois de cada correção: corrigir o preço tira a marca de "fora do padrão".
- As marcas de fora do padrão, ambígua e sugestão de Conteúdo **não** impedem a confirmação. A Oferta sem preço continua impedindo (ticket 06).

## Erros (mensagens em português)

- Confirmar com uma Oferta marcada como fora do padrão: a confirmação passa.
- Confirmar com uma Oferta sem preço continua recusado → `Informe um preço maior que zero antes de confirmar. Ofertas sem preço: 1003.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com descrições e preços inventados escolhidos para cada regra: um preço fora do padrão, uma descrição com "KIT", uma com "C/3", um Catálogo com só 3 preços e um PDF com um preço que o leitor não transforma em Oferta (para M < N).
- Nenhum fake da LLM.

## Fora deste ticket

- Contagem nos caminhos de tabela (21) e LLM (25).
