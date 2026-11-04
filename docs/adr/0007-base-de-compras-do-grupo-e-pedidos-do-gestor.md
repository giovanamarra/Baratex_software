---
status: accepted
---

# A base de compras é do grupo; Lojas e Pedidos são de cada Gestor

Os sócios do grupo compram dos mesmos Fornecedores. Se cada Gestor tivesse seus próprios Catálogos, o mesmo arquivo seria importado várias vezes e nada poderia ser comparado entre eles. Decidimos que Fornecedor, Perfil do Fornecedor, Catálogo, Oferta, Produto e Teto de compra pertencem ao grupo e são vistos e editados por todos os Gestores. Lojas e Pedidos pertencem a um Gestor.

## Regras

- Um Pedido só inclui Lojas do Gestor que o criou, e só esse Gestor pode editá-lo.
- Mudanças em dados do grupo que afetam a comparação ficam registradas com autor e data: Perfil do Fornecedor, vínculo entre Oferta e Produto, e Conteúdo.
- Consultar o Pedido de outro Gestor fica fora do MVP; o modelo não impede essa evolução.

## Opções consideradas

- **Tudo por Gestor:** isolamento total, mas importação duplicada e nenhuma comparação entre Gestores.

## Consequências

A mudança que um Gestor faz no Perfil, no vínculo de um Produto ou no Conteúdo vale para todos. No MVP, com praticamente uma usuária, o risco é baixo; com mais sócios ativos, pode ser preciso restringir quem altera esses dados.
