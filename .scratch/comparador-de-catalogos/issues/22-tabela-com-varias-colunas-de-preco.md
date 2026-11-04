# 22 — Catálogo em tabela com várias colunas de preço

Status: ready-for-agent
Type: task
Blocked by: 21
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Tabela: a menor de cada linha, Catálogo "sem desconto")
ADRs: ADR-0006 (vale a menor; não pergunta desconto)
User stories: 19, 24

## O que entrega

Num Catálogo com preços por prazo ou por faixa, vale sempre a menor coluna de cada linha, e a Importação não pede desconto, para não aplicá-lo duas vezes.

## Critérios de aceite

- O mapeamento aceita mais de uma coluna de preço.
- O preço impresso de cada Oferta é o menor valor entre as colunas de preço da linha, ignorando células vazias (19).
  - Exemplo: 12,00 / 11,40 / (vazio) → 11,40.
- O Catálogo fica marcado como "sem desconto": a Importação não pede desconto, e a Revisão não mostra o campo (24).
- A confirmação não exige o desconto nesse Catálogo. É a exceção à regra do ticket 06 ("Informe o desconto do Catálogo antes de confirmar"), registrada no spec.
- A contagem de preços conta as linhas com algum preço, não cada célula.
- O mapeamento com várias colunas de preço fica guardado no Perfil, como no ticket 21.

## Erros (mensagens em português)

- Informar desconto numa Revisão desse Catálogo → `Este Catálogo tem várias colunas de preço e já usa a menor de cada linha. Não informe desconto, para não aplicá-lo duas vezes.`

## O que o teste precisa

- Catálogo fictício em tabela Excel com três colunas de preço inventadas (ex.: "À vista", "30 dias", "60 dias") e uma linha com uma das colunas vazia.
- Nenhum fake da LLM.
