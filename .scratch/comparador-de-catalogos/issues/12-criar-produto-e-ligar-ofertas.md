# 12 — Criar Produto e ligar Ofertas a ele

Status: ready-for-agent
Type: task
Blocked by: 09
Spec: [docs/spec.md](../../../docs/spec.md) (Produtos e comparação; Modelo de dados › vínculo Oferta → Produto; Revisão › a confirmação aplica o vínculo guardado)
ADRs: ADR-0003 (Produto definido pela gestora; vínculo por Fornecedor + código), ADR-0007 (auditoria)
User stories: 40, 59, 60, 61, 62, 63, 64, 68, 69

## O que entrega

A gestora cria Produtos com o nome que quiser e, a partir da busca, liga a eles Ofertas de Fornecedores diferentes. O vínculo vale para os Catálogos futuros.

## Critérios de aceite

- Criar Produto (nome), renomear e listar os Produtos em ordem alfabética (59, 68). Todos os Gestores veem os mesmos Produtos.
- Ligar uma Oferta a um Produto a partir dos resultados da busca (60). Ofertas de Fornecedores diferentes, mesmo só semelhantes, podem estar no mesmo Produto (61).
- O vínculo é guardado por Fornecedor + código (63). Ofertas com o mesmo código em Catálogos anteriores desse Fornecedor também passam a estar ligadas.
- Numa Importação nova do mesmo Fornecedor, a Oferta com esse código já aparece ligada ao Produto na Revisão e continua ligada depois de confirmar (40).
- Desligar uma Oferta de um Produto desfaz o vínculo do Fornecedor + código (62).
- O histórico de vínculos de um Produto lista Gestor, data, "ligou" ou "desligou", Fornecedor e código (64).
- A busca mostra o Produto de cada Oferta, quando houver. Ofertas sem Produto continuam aparecendo (69).
- Cada Fornecedor + código fica em, no máximo, um Produto.

## Erros (mensagens em português)

- Nome de Produto vazio → `Dê um nome ao Produto.`
- Nome repetido (ignorando maiúsculas) → `Já existe um Produto chamado Tesoura.`
- Ligar um código que já está em outro Produto → `O código 1001 do Fornecedor Alfa já está ligado ao Produto Tesoura. Desligue antes de ligar a outro.`
- Desligar uma Oferta que não está ligada → `Esta Oferta não está ligada a nenhum Produto.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Fornecedores; dois Catálogos do mesmo Fornecedor em dias diferentes; dois Gestores.
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- A comparação lado a lado (13). A evolução de preço do Produto (28).
- Sugestão automática de vínculo; distinção entre Produto idêntico e semelhante (Out of Scope).
