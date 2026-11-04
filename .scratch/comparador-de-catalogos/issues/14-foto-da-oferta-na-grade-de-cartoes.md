# 14 — Foto da Oferta lida da grade de cartões

Status: ready-for-agent
Type: task
Blocked by: 13
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Foto; Modelo de dados › Oferta: foto opcional)
ADRs: ADR-0006 (foto é opcional; arquivo de preços é o Catálogo)
User stories: 57 (foto), 65 (foto)

## O que entrega

Quando o cartão do Catálogo tem foto, ela aparece na Revisão, na busca e na comparação do Produto, para a gestora reconhecer o produto sem abrir o arquivo.

## Critérios de aceite

- Um cartão do Layout A com imagem gera uma Oferta proposta com foto, visível na Revisão.
- Ao confirmar, a foto fica guardada (no armazenamento de arquivos, para sempre) e aparece nos resultados da busca (57) e na comparação do Produto (65).
- Um cartão sem imagem gera uma Oferta sem foto, sem erro nem marca.
- A foto não entra em nenhum cálculo nem em nenhuma comparação.

## Erros (mensagens em português)

- PDF só com fotos, sem preços → `Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.` (o spec não importa arquivo só de fotos)

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, agora com imagem opcional por cartão: uma imagem pequena gerada no próprio teste (por exemplo, um quadrado colorido).
- Nenhum fake da LLM.

## Fora deste ticket

- Ligar fotos de um arquivo separado só de fotos (Out of Scope).
- Fotos nos caminhos de tabela e LLM (não há ticket; ver o resumo do /to-tickets).
