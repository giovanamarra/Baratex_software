# 33 — Aviso de Catálogo mais antigo e correção da data de um Catálogo confirmado

Status: ready-for-agent
Type: task
Blocked by: 31
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › Data do Catálogo, Corrigir a data; Modelo de dados › Catálogo, Auditoria)
ADRs: ADR-0009 (itens 5 e 6), ADR-0007 (auditoria)
User stories: 103, 104, 105
Muda código já feito: ticket 04 (o Catálogo confirmado deixa de ser imutável na data). O ticket continua resolvido.

## O que entrega

A Revisão avisa quando o Catálogo informado é mais antigo que o último do Fornecedor. Depois de confirmado, qualquer Gestor pode corrigir uma data errada, vendo antes quantas Ofertas mudam de vigência, e fica registrado quem corrigiu.

## Critérios de aceite

Aviso na Revisão (103)

- Com a data informada anterior à data do Catálogo confirmado mais recente do mesmo Fornecedor, a Revisão mostra o aviso abaixo. Ele **não bloqueia** a confirmação.
- Com a mesma data, ou mais recente, não há aviso. Um Fornecedor sem Catálogos não tem aviso.
- Catálogos de outro Fornecedor não contam. A comparação usa a regra de ordenação do ticket 31 (só mês e ano = dia 1).

Corrigir a data (104)

- Pela página do Catálogo, qualquer Gestor (não só quem importou) corrige a data do Catálogo, com as mesmas regras de formato, data futura e ano do ticket 31 e o mesmo aviso de Catálogo mais antigo (comparando com os **outros** Catálogos do Fornecedor).
- Antes de salvar, a gestora vê o impacto na vigência das Ofertas **deste** Catálogo: quantas passam a ser vigentes ou quantas deixam de ser. Só depois de confirmar o aviso a data muda.
  - Exemplo: o Catálogo de 15/10/2026 tem 40 Ofertas, 37 delas vigentes; corrigir para 10/2025, com outro Catálogo de 01/09/2026 que tem esses 37 códigos → `Com a nova data, 37 Ofertas deste Catálogo deixam de ser vigentes.`
- Depois de corrigir, a busca, a lista de Catálogos e a vigência usam a nova data, sem outro passo.
- A data é o **único** dado do Catálogo que muda depois da confirmação. O dia da Importação não muda.
- Informar a mesma data que já está guardada não é correção: nada é registrado.

Registro (105)

- Cada correção guarda o Gestor, o dia da correção, a data anterior e a data nova, como foram informadas (`10/2026`, `15/10/2026`).
- A página do Catálogo lista as correções, da mais recente para a mais antiga.

## Erros (mensagens em português)

- Aviso, sem bloquear: `Este Catálogo é mais antigo que o de 15/10/2026 deste Fornecedor: os códigos que estão nos dois continuam com o preço do mais recente.`
- Impacto (texto proposto para os casos que o spec não escreve):
  - `Com a nova data, 37 Ofertas deste Catálogo deixam de ser vigentes.`
  - `Com a nova data, 12 Ofertas deste Catálogo passam a ser vigentes.`
  - `Com a nova data, nenhuma Oferta deste Catálogo muda de vigência.`
- Formato, data futura e ano: as mesmas mensagens do ticket 31.
- Corrigir um Catálogo que não existe → `Catálogo não encontrado.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; três Catálogos do mesmo Fornecedor com datas diferentes e códigos em comum; um Catálogo de outro Fornecedor; dois Gestores (o que corrige não é o que importou).
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- Linhas de Pedido que deixam de ser vigentes por causa da correção (40).
- Desfazer uma correção (o registro basta; ADR-0007).
