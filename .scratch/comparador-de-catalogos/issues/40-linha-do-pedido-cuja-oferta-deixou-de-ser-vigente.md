# 40 — Linha do Pedido cuja Oferta deixou de ser vigente

Status: ready-for-agent
Type: task
Blocked by: 16, 33
Spec: [docs/spec.md](../../../docs/spec.md) (Modelo de dados › Pedido: a linha nunca troca de Oferta sozinha)
ADRs: ADR-0009 (Consequências), ADR-0004
User stories: 108

## O que entrega

Quando chega um Catálogo mais recente (ou a data de um Catálogo é corrigida) e uma Oferta do Pedido deixa de ser vigente, a linha fica marcada com o preço mais recente. A gestora decide se troca. O sistema nunca muda o preço do Pedido sozinho.

## Critérios de aceite

- Uma linha cuja Oferta não é mais vigente aparece marcada no Pedido, com o Preço unitário e a data do Catálogo da Oferta vigente do mesmo Fornecedor + código.
- A marca é calculada na consulta: corrigir a data (ticket 33) de modo que a Oferta da linha volte a ser vigente tira a marca, sem outro passo.
- A linha continua apontando para a Oferta escolhida, com o mesmo preço e o mesmo valor, até a gestora trocar.
- **Usar a Oferta vigente** troca a Oferta da linha pela vigente e **mantém as Caixas** de cada Loja (decisão da usuária, 2026-11-05). As Unidades de venda são recalculadas com a Caixa nova.
  - Exemplo: Loja Centro com 2 Caixas de 48 (96 Unidades de venda); a vigente tem Caixa 24 → 2 Caixas de 24 (48 Unidades de venda), com o aviso de Caixa mudada.
  - Se as quantidades com a Caixa nova não respeitarem o Fracionamento ou o mínimo do Fornecedor (ticket 17), a troca é recusada com a mensagem de sempre, e a linha fica como estava.
- A marca não bloqueia a exportação. A exportação sai com a Oferta da linha, como está.
- Pedidos de outro Gestor continuam inacessíveis (ticket 16).

## Erros (mensagens em português)

- Marca da linha → `Há um preço mais recente deste código: R$ 11,00 (Catálogo de 15/11/2026).` (Preço unitário da Oferta vigente)
- Depois da troca com Caixa diferente (texto proposto) → `A Caixa mudou de 48 para 24: confira as quantidades.`
- Texto proposto: a Oferta vigente já é outra linha do mesmo Pedido → `A Oferta vigente já está neste Pedido. Remova esta linha ou altere a quantidade na outra.`
- Usar a Oferta vigente numa linha que já é vigente → `Esta linha já usa a Oferta vigente.`
- Fracionamento ou mínimo: as mensagens dos tickets 15 e 17.

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Catálogos do mesmo Fornecedor com datas diferentes e o mesmo código com Caixas diferentes; um Gestor com duas Lojas; um Perfil com Fracionamento e mínimo.
- Pedido montado pelos casos de uso (15, 16) e uma correção de data (33).
- Nenhum fake da LLM.

## Fora deste ticket

- Trocar a linha automaticamente ou bloquear a exportação (opções recusadas na Q11 do grill).
