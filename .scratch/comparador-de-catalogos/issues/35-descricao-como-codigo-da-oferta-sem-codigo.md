# 35 — Descrição normalizada como código da Oferta sem código

Status: ready-for-agent
Type: task
Blocked by: 12, 18, 32
Spec: [docs/spec.md](../../../docs/spec.md) (Modelo de dados › Código, Conteúdo, vínculo Oferta → Produto, Oferta vigente)
ADRs: ADR-0010 (item 7), ADR-0003 (vínculo pela descrição normalizada quando não há código)
User stories: 63 (sem código), 88 (código vazio), 114 (a chave; o mapeamento sem coluna de código é do ticket 21)
Muda código já feito: tickets 06 (Oferta sem código na Revisão), 07 (Conteúdo pela chave), 08 (sugestão e "Manter 1" pela chave) e 09 (vigência e busca pela chave). Esses tickets continuam resolvidos.

## O que entrega

Uma Oferta pode não ter código do Fornecedor. Nesse caso, a descrição normalizada faz o papel de código: vigência, Conteúdo, vínculo de Produto, código repetido e histórico usam essa chave. É o que permite importar Fornecedores que não usam código.

## Critérios de aceite

A chave

- O **código** de uma Oferta é o código do Fornecedor ou, quando ela não tem código, a **descrição normalizada**: sem acento, sem maiúsculas, sem espaços nas pontas e sem espaços duplicados.
  - `Balde  Azul 10L` e `balde azul 10l` são o mesmo item; `Balde Azul 10 L` é outro.
- As duas formas **nunca se misturam**: uma Oferta sem código com descrição `1001` não casa com a Oferta de código `1001` do mesmo Fornecedor.
- A chave é calculada da descrição como confirmada. Corrigir a descrição na Revisão muda a chave.

Na Revisão

- Adicionar e corrigir Oferta aceitam código vazio; a descrição continua obrigatória.
- As mensagens de confirmação recusada que listam Ofertas pelo código mostram a descrição quando a Oferta não tem código (`Ofertas sem Caixa: 1001, Balde Azul 10L.`).
- A marca "código repetido" (ticket 32) vale para descrições iguais pela chave.

Depois de confirmar

- **Vigência:** duas Ofertas sem código, de Catálogos com datas diferentes, com a mesma chave → só a do mais recente é vigente (regra do ticket 31).
- **Conteúdo:** definir o Conteúdo de uma Oferta sem código vale para a mesma chave nos próximos Catálogos; a sugestão de Conteúdo e o "Manter 1" do ticket 08 seguem a chave.
- **Produto:** ligar uma Oferta sem código a um Produto guarda o vínculo pela chave; a mesma descrição num Catálogo novo já chega ligada (histórias 40 e 63).
- **Busca:** encontra a Oferta sem código pela descrição; a coluna de código fica vazia.
- **Exportação do Pedido** (88): a coluna `CÓD.` sai vazia para a Oferta sem código, e a descrição identifica o item.
- Consequência aceita (ADR-0010): uma descrição que muda uma vírgula vira outro item, sem Conteúdo, Produto nem histórico. Não há tentativa de ligar por semelhança.

## Erros (mensagens em português)

- Adicionar ou corrigir Oferta sem descrição → `Informe a descrição da Oferta.` (substitui `Informe o código e a descrição da Oferta.` do ticket 06)
- Definir o Conteúdo fora da Revisão de uma descrição sem Oferta → `O Fornecedor Alfa não tem Oferta com a descrição "Balde Azul 10L".`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A e Ofertas sem código criadas pela Revisão (adicionar à mão ou corrigir o código para vazio), porque o leitor de tabela sem código só chega no ticket 21.
- Dois Catálogos do mesmo Fornecedor em datas diferentes; um Produto (ticket 12); um Pedido exportado (ticket 18).
- Nenhum fake da LLM.

## Fora deste ticket

- Mapeamento de planilha sem coluna de código e descrição em várias colunas (21).
- Ligar foto por descrição (38).
- Ligar por semelhança aproximada (Out of Scope).
