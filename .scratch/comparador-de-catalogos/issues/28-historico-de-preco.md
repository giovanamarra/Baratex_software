# 28 — Histórico de preço de uma Oferta e evolução do Produto por Fornecedor

Status: ready-for-agent
Type: task
Blocked by: 12, 31
Spec: [docs/spec.md](../../../docs/spec.md) (Histórico de preço; Casos de uso › histórico de preço de uma Oferta, evolução de preço do Produto por Fornecedor; Modelo de dados › Oferta vigente)
ADRs: ADR-0003 (só Produtos entram no histórico por Produto), ADR-0005, ADR-0009 (ordem pela data do Catálogo)
User stories: 70, 71, 72, 73
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora vê se o preço de uma Oferta subiu ou caiu ao longo dos Catálogos e compara, ao longo do tempo, os Fornecedores de um Produto.

## Critérios de aceite

- Histórico de preço de uma Oferta (Fornecedor + código, ou a descrição normalizada quando não há código, ticket 35) lista, do Catálogo mais antigo ao mais recente **pela data do Catálogo** (não pelo dia da Importação): data do Catálogo como foi informada, preço impresso, desconto e Preço unitário. Funciona com ou sem Produto (72).
- Um Catálogo antigo importado depois entra no seu lugar pela data do Catálogo, e não no fim.
- Só mês e ano conta como o dia 1 do mês para ordenar (ticket 31), e aparece como foi informado (`10/2026`).
- Com dois Catálogos do mesmo Fornecedor com a mesma data, o histórico mostra um ponto por data, escolhido pela mesma regra da Oferta vigente: o Catálogo **confirmado por último** e, dentro dele, a de menor Preço unitário (tickets 31 e 32). A regra antiga (menor Preço unitário entre os dois Catálogos) deixa de valer.
- Uma data corrigida (ticket 33) muda a posição do ponto, sem outro passo.
- A evolução de preço de um Produto devolve uma série por Fornecedor + código ligado, com (data do Catálogo, Preço unitário) (71). Duas séries de Fornecedores diferentes, lado a lado, permitem ver quem costuma ser mais barato (73).
- Importar um Catálogo novo acrescenta um ponto e não apaga os anteriores (70).
- Mudar o Conteúdo de um Fornecedor + código muda todos os pontos dele, como no ticket 07.

## Erros (mensagens em português)

- Código sem Ofertas → `O Fornecedor Alfa não tem Oferta com o código 9999.`
- Produto que não existe → `Produto não encontrado.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Fornecedores; três Catálogos em datas do Catálogo diferentes (um deles importado depois dos outros, com data mais antiga, e um só com mês e ano) e dois com a mesma data, o mais caro confirmado por último; um Produto com Ofertas dos dois Fornecedores.
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- O painel com gráfico (30).
