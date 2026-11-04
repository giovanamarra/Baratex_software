# 04 — Confirmar ou abandonar a Revisão

Status: resolved
Type: task
Blocked by: 03
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão; Modelo de dados › Catálogo)
ADRs: ADR-0006 (nada é salvo sem Revisão), ADR-0007
User stories: 15, 38, 39, 58, 70

## O que entrega

A gestora confirma a Revisão e o Catálogo passa a existir, com data e Ofertas, ou abandona e nada fica salvo. Ela vê os Catálogos de cada Fornecedor com a data.

## Critérios de aceite

- Antes de confirmar, nada é salvo como Catálogo: com uma Revisão em andamento, o Fornecedor continua sem Catálogos (veio do ticket 03).
- Confirmar a Revisão cria, de uma vez só (transação única), o Catálogo e as suas Ofertas. O Catálogo guarda o Fornecedor, a data, o Gestor que importou, o arquivo de origem e as Condições do Catálogo (vazias neste ticket).
- A data do Catálogo é o dia em que a Importação começou: uma Importação iniciada no dia 10 e confirmada no dia 11 gera um Catálogo do dia 10 (15).
- Listar os Catálogos de um Fornecedor mostra o Catálogo confirmado, com a data (58).
- Duas Importações do mesmo Fornecedor, em dias diferentes, geram dois Catálogos. O primeiro e as suas Ofertas continuam intactos (70).
- Depois de confirmada, a Revisão deixa de aparecer entre as Revisões em andamento.
- Abandonar a Revisão não cria Catálogo nem Oferta, tira a Revisão da lista e apaga o arquivo enviado (39).

## Erros (mensagens em português)

- Confirmar uma Revisão já confirmada → `Esta Revisão já foi confirmada.`
- Confirmar ou abandonar uma Revisão que não existe mais → `Esta Revisão não existe mais. Comece uma nova Importação.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A (ticket 03).
- Controle do dia no teste (relógio injetável ou data congelada), para simular Importações em dias diferentes.
- Nenhum fake da LLM.

## Fora deste ticket

- Regras que recusam a confirmação (Caixa, preço, páginas da LLM): tickets 06 e 26.
- Aplicar o Conteúdo e o vínculo de Produto já guardados: tickets 07 e 12.

## Comments

**2026-11-04 — implementado por TDD** (commits `03f067d` a `a73aff8`)

- **Casos de uso:** `confirmar_revisao`, `abandonar_revisao` (`importacao/casos_de_uso.py`); `registrar_catalogo`, `listar_catalogos_do_fornecedor` (`catalogos/casos_de_uso.py`). `iniciar_importacao` ganhou `hoje=` (padrão: dia local) para os testes simularem dias.
- **Modelo:** `Catalogo` (Fornecedor, Gestor que importou, data, arquivo de origem) e `Oferta` no módulo Catálogos. A Revisão guarda `iniciada_em` e o `catalogo` que gerou; sem Catálogo, está em andamento. O Catálogo aponta para o mesmo arquivo guardado na Revisão.
- **Decisões da usuária:** abandonar uma Revisão já confirmada é recusado com `Esta Revisão já foi confirmada.`; a falha da transação é provocada por uma regra real no banco (preço impresso nunca negativo; vazio permitido), sem mock.
- **Transação única:** testada com `TransactionTestCase` (o `TestCase` esconderia a falta de transação). Dois vermelhos registrados: sem a regra a Oferta negativa entrava; com a regra e sem transação o Catálogo ficava salvo pela metade.
- **Lista de Catálogos:** do mais recente para o mais antigo (no mesmo dia, o último confirmado primeiro).
- **Autorização:** só quem iniciou confirma ou abandona (caso de uso e cliente HTTP, 403).
- **Condições do Catálogo:** nenhum campo criado ainda; o desconto entra no ticket 05, onde tem comportamento para testar.
- Ofertas sem preço ou sem Caixa continuam confirmáveis; o bloqueio é do ticket 06.
