# 09 — Buscar Ofertas vigentes com Preço unitário

Status: resolved
Type: task
Blocked by: 05, 07
Spec: [docs/spec.md](../../../docs/spec.md) (Ofertas vigentes e busca; Modelo de dados › Oferta vigente; Base comum do grupo)
ADRs: ADR-0007 (base do grupo), ADR-0005
User stories: 52, 53, 54, 55, 56, 57 (sem foto), 69, 98, 99

## O que entrega

A gestora acha qualquer Oferta por código ou trecho da descrição, em todos os Catálogos do grupo, e vê o Preço unitário atual de cada Fornecedor.

## Critérios de aceite

- Buscar Ofertas (texto, Fornecedor opcional, só vigentes = sim por padrão) encontra por código ou por trecho da descrição, ignorando maiúsculas e acentos (52).
- Cada resultado mostra código, descrição, Preço unitário, Caixa, Fornecedor e data do Catálogo (57).
- **Oferta vigente** (54): o Fornecedor Alfa tem o código 1001 num Catálogo do dia 01 (10,00) e num do dia 15 (11,00). A busca padrão mostra só a de 11,00. Com "só vigentes = não", mostra as duas (53).
- **Mesmo dia** (55): dois Catálogos do Fornecedor Alfa do dia 15 têm o código 1001, um a 10,50 sem desconto e outro a 11,00 com 10% (Preço unitário 9,90). Vale a de 9,90, porque o desempate é pelo Preço unitário.
- O filtro por Fornecedor mostra só as Ofertas dele (56).
- Uma Oferta sem Produto aparece na busca (69).
- Um Catálogo importado pelo Gestor B aparece na busca do Gestor A (98, 99).
- Nos resultados, a tela oferece "definir Conteúdo", usando o caso de uso do ticket 07.

## Erros (mensagens em português)

- Texto vazio e sem Fornecedor → `Digite um código ou parte da descrição, ou escolha um Fornecedor.`
- Uma busca sem resultados não é erro: devolve lista vazia, e a tela diz `Nenhuma Oferta encontrada.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Fornecedores; três Catálogos em dois dias diferentes, com descrições acentuadas inventadas; dois Gestores.
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- Destaque do Teto de compra (10). Foto (14). Produto do resultado (12).

## Comments

**Resolução (2026-11-05)**

- **Caso de uso:** `buscar_ofertas(gestor, texto, fornecedor=None, so_vigentes=True)` devolve `ResultadoDaBusca(ofertas, total)`; `ofertas` tem no máximo `LIMITE_DE_RESULTADOS` (200), ordenadas por Fornecedor, código e Catálogo mais recente.
- **Busca sem maiúsculas e sem acentos:** a Oferta guarda `busca` (código, quebra de linha e descrição, normalizados por `catalogos/busca.py`), preenchido em `registrar_catalogo`. A migração 0009 preenche as Ofertas existentes; a 0010 cria o índice em `codigo`.
- **Oferta vigente:** calculada no banco, sem gravar o Preço unitário. Dentro de um Fornecedor + código o Conteúdo é o mesmo, então o desempate do mesmo dia compara preço impresso × (100 − desconto). Se o valor empatar, vale o Catálogo confirmado por último.
- **Tela:** "Buscar" na barra; campo de texto, filtro de Fornecedor, "Mostrar também Ofertas antigas"; tabela com "Definir Conteúdo"; avisos de limite, de lista vazia e de erro.
- **Medição com 100 mil Ofertas** (20 Fornecedores × 5 Catálogos × 1.000 códigos próprios, SQLite): trecho comum, só vigentes ~150 ms; letra "a" (casa com todas), só vigentes ~420 ms; sem filtro de vigência ~35 ms. Pior caso artificial, com todos os Fornecedores repetindo os mesmos códigos (100 Ofertas por código): ~1,9 s num trecho comum e ~7,4 s com a letra "a".
