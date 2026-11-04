# 06 — Corrigir, adicionar e remover Ofertas na Revisão

Status: resolved
Type: task
Blocked by: 05
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › confirmação recusada; Extração › marcas de conferência)
ADRs: ADR-0006 (Oferta sem Caixa não é confirmada)
User stories: 30 (preço ausente ou zero), 31, 34, 35, 36

## O que entrega

A gestora conserta erros de leitura antes de salvar. A confirmação é recusada enquanto houver Oferta sem Caixa ou sem preço válido.

## Critérios de aceite

- Corrigir uma Oferta proposta (código, descrição, preço impresso, Caixa, Embalagem intermediária) faz a Revisão mostrar o valor novo e recalcula o Preço unitário (34).
- Adicionar uma Oferta à mão faz ela aparecer na Revisão com o caminho "manual" (35).
- Remover uma Oferta proposta tira ela da Revisão, e ela não entra no Catálogo (36).
- Uma Oferta sem preço ou com preço zero fica marcada (30).
- A confirmação é recusada enquanto houver Oferta sem Caixa. Depois que a gestora informa a Caixa, a confirmação passa (31).
- A confirmação é recusada enquanto houver Oferta sem preço maior que zero.
- As correções só chegam ao Catálogo com a confirmação. Abandonar a Revisão descarta todas.

## Erros (mensagens em português)

- Confirmar com Oferta sem Caixa → `Informe a Caixa antes de confirmar. Ofertas sem Caixa: 1001, 1007.`
- Confirmar com Oferta sem preço válido → `Informe um preço maior que zero antes de confirmar. Ofertas sem preço: 1003.`
- Corrigir com preço negativo ou zero → `O preço precisa ser maior que zero.`
- Caixa zero, negativa ou fracionária → `A Caixa precisa ser um número inteiro de Unidades de venda, maior que zero.`
- Adicionar Oferta sem código ou sem descrição → `Informe o código e a descrição da Oferta.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com um cartão sem Caixa e um cartão sem preço.
- Nenhum fake da LLM.

## Fora deste ticket

- Preço fora do padrão, Unidade de venda ambígua, sugestão de Conteúdo e contagem de preços (08).

## Comments

**2026-11-04 — implementado por TDD** (commits `ac3e1c3` a `11e6f69`)

- **Casos de uso** (`importacao/casos_de_uso.py`): `corrigir_oferta_proposta`, `adicionar_oferta_proposta` (caminho "manual", no fim da lista), `remover_oferta_proposta`, `obter_oferta_proposta` (para os formulários). Valores entram como a gestora digita: preço "1.234,56" ou "9,90", Caixa "24"; vazio = ausente (a confirmação recusa depois). Todos passam pelas recusas da Revisão (de outro Gestor, já confirmada).
- **Marcas** (`OfertaProposta.marcas`, derivadas): "sem preço" e "preço zero". O ticket 08 acrescenta as outras.
- **Confirmação** recusa, numa mensagem só e com os códigos: Oferta sem Caixa; Oferta sem preço maior que zero; desconto não informado.
- **Embalagem intermediária** (decisão da usuária): fora deste ticket. O Layout A não tem o campo; ele entra com o primeiro caminho que o trouxer (Layout B ou tabela).
- **Desconto obrigatório** (decisão da usuária, vinda do grill): a confirmação é recusada enquanto o desconto da Revisão não for informado; 0 vale como resposta. Mensagem: `Informe o desconto do Catálogo antes de confirmar. Se não houver desconto, informe 0.` Spec e GLOSSARY atualizados (`d26ca7f`). A exceção dos Catálogos com várias colunas de preço fica para o ticket 22.
- **Código e descrição** obrigatórios também ao corrigir (Oferta sem código não pode existir).
- **Teste de transação do ticket 04** (decisão da usuária): a validação passou a recusar a Oferta de R$-5,00 antes do banco; a falha agora vem de um gatilho no SQLite de teste que recusa gravar a Oferta 1002 depois de o Catálogo ser criado. Sem a transação, o teste falha (provado com mutação).
- Testes do ticket 04 que confirmavam sem desconto ou com cartões mascarados foram ajustados na preparação; o que provam não mudou.
- **Telas:** Corrigir e Remover por linha (Remover com confirmação e botão de perigo), "Adicionar Oferta" abaixo da tabela, linhas de alerta com texto. Confirmação recusada volta para a Revisão.
