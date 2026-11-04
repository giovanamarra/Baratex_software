# 28 — Histórico de preço de uma Oferta e evolução do Produto por Fornecedor

Status: ready-for-agent
Type: task
Blocked by: 12
Spec: [docs/spec.md](../../../docs/spec.md) (Histórico de preço; Casos de uso › histórico de preço de uma Oferta, evolução de preço do Produto por Fornecedor)
ADRs: ADR-0003 (só Produtos entram no histórico por Produto), ADR-0005
User stories: 70, 71, 72, 73

## O que entrega

A gestora vê se o preço de uma Oferta subiu ou caiu ao longo dos Catálogos e compara, ao longo do tempo, os Fornecedores de um Produto.

## Critérios de aceite

- Histórico de preço de uma Oferta (Fornecedor + código) lista, do Catálogo mais antigo ao mais recente: data do Catálogo, preço impresso, desconto e Preço unitário. Funciona com ou sem Produto (72).
- Com dois Catálogos do mesmo Fornecedor no mesmo dia, o histórico mostra um ponto por dia, escolhido pela mesma regra da Oferta vigente (menor Preço unitário).
- A evolução de preço de um Produto devolve uma série por Fornecedor + código ligado, com (data, Preço unitário) (71). Duas séries de Fornecedores diferentes, lado a lado, permitem ver quem costuma ser mais barato (73).
- Importar um Catálogo novo acrescenta um ponto e não apaga os anteriores (70).
- Mudar o Conteúdo de um Fornecedor + código muda todos os pontos dele, como no ticket 07.

## Erros (mensagens em português)

- Código sem Ofertas → `O Fornecedor Alfa não tem Oferta com o código 9999.`
- Produto que não existe → `Produto não encontrado.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Fornecedores; três Catálogos em datas diferentes e dois no mesmo dia; um Produto com Ofertas dos dois Fornecedores.
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- O painel com gráfico (30).
