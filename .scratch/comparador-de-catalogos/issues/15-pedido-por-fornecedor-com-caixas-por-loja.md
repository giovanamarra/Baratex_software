# 15 — Pedido para um Fornecedor, com Caixas por Loja

Status: ready-for-agent
Type: task
Blocked by: 02, 09, 31
Spec: [docs/spec.md](../../../docs/spec.md) (Pedidos; Modelo de dados › Pedido)
ADRs: ADR-0007 (Pedido é do Gestor; só Lojas dele), ADR-0004 (Ofertas vigentes de vários Catálogos do mesmo Fornecedor), ADR-0009 (data do Catálogo ao incluir)
User stories: 5, 74, 75, 77, 79, 80, 99, 107 (ao incluir)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora cria um Pedido para um Fornecedor, adiciona Ofertas vigentes de qualquer Catálogo dele e informa quantas Caixas vão para cada uma das suas Lojas. Ela vê, por Loja, as Unidades de venda e o valor.

## Critérios de aceite

- Criar Pedido (Gestor, Fornecedor) gera um Pedido desse Gestor, com a data de criação (74).
- Adicionar ao Pedido Ofertas vigentes de dois Catálogos diferentes do mesmo Fornecedor, inclusive de um Catálogo importado por outro Gestor (75, 99). "Vigente" segue a regra do ticket 31 (Catálogo de data mais recente; mesma data, o confirmado por último).
- Ao escolher a Oferta para incluir, a tela mostra a data do Catálogo de cada Oferta, como foi informada (107).
- Definir as quantidades de uma linha (Caixas por Loja, todas as Lojas de uma vez) guarda a quantidade em Unidades de venda: 2 Caixas de 48 → 96 (77).
- Ver o Pedido mostra, por Loja, as Unidades de venda e o valor (80):
  - valor da linha = Unidades de venda × preço impresso;
  - total da Loja = soma das linhas, com o desconto das Condições do Catálogo de cada linha aplicado.
  - Exemplo: 96 × 2,00 = 192,00; com 5% de desconto, total da Loja 182,40.
- Um Fornecedor sem Perfil não permite Fracionamento.

## Erros (mensagens em português)

- Oferta de outro Fornecedor → `Esta Oferta é do Fornecedor Beta, e o Pedido é do Fornecedor Alfa.`
- Oferta que não é mais vigente → `Esta Oferta não é mais vigente: o Fornecedor Alfa tem um Catálogo mais recente para o código 1001.`
- Loja de outro Gestor → `A Loja Norte não é sua. Um Pedido só aceita as suas Lojas.` (5)
- Caixas fracionárias sem Fracionamento (0,5) → `O Fornecedor Alfa não permite Fracionamento: informe um número inteiro de Caixas.` (79)
- Caixas negativas → `A quantidade não pode ser negativa.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Catálogos vigentes do mesmo Fornecedor (um com desconto); um Catálogo de outro Fornecedor; dois Gestores com Lojas.
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- Editar e remover linhas, observação, lista de Pedidos, privacidade e Teto no Pedido (16). Fracionamento (17). Exportação (18).
- Linha cuja Oferta deixou de ser vigente depois de incluída (40).
- Desconto por arquivo de preços no total da Loja (37: até lá, o desconto de cada linha é o do seu Catálogo).
