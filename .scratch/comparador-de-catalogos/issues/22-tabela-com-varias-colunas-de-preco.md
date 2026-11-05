# 22 — Catálogo em tabela com várias colunas de preço

Status: ready-for-agent
Type: task
Blocked by: 21, 37
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Tabela: a menor de cada linha; o desconto continua sendo perguntado)
ADRs: ADR-0006 (vale a menor), ADR-0010 (item 9: o desconto é sempre perguntado, com aviso; substitui o "não pergunta desconto" do ADR-0006)
User stories: 19, 24 (nova versão: o aviso)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

Num Catálogo com preços por prazo ou por faixa, vale sempre a menor coluna de cada linha. O desconto continua sendo pedido, mas o campo avisa que essa coluna pode já ter desconto, para a gestora não aplicá-lo duas vezes.

## Critérios de aceite

- O mapeamento aceita mais de uma coluna de preço.
- O preço impresso de cada Oferta é o menor valor entre as colunas de preço da linha, ignorando células vazias (19).
  - Exemplo: 12,00 / 11,40 / (vazio) → 11,40.
- Só as colunas marcadas como preço entram na menor (uma coluna de preço sugerido de venda, não marcada, nunca é a menor).
- O desconto do arquivo é pedido e obrigatório como em qualquer arquivo de preços (tickets 05 e 37); 0 vale. **Não** existe mais a marca de Catálogo "sem desconto" nem a exceção na confirmação.
- O campo de desconto desse arquivo mostra o aviso abaixo (24). O aviso não bloqueia e não muda o cálculo.
- Num Catálogo com duas planilhas de preços, só a planilha com várias colunas de preço tem o aviso.
- A contagem de preços conta as linhas com algum preço, não cada célula.
- O mapeamento com várias colunas de preço fica guardado no Perfil, como no ticket 21.

## Erros (mensagens em português)

- Aviso no campo de desconto (texto proposto) → `Este arquivo tem várias colunas de preço, e vale a menor de cada linha. Ela pode já ter desconto: confira antes de informar outro, para não aplicá-lo duas vezes.`
- A recusa `Este Catálogo tem várias colunas de preço e já usa a menor de cada linha. Não informe desconto...` saiu (ADR-0010).

## O que o teste precisa

- Catálogo fictício em tabela Excel com três colunas de preço inventadas (ex.: "À vista", "30 dias", "60 dias"), uma linha com uma das colunas vazia e uma coluna de preço sugerido não marcada.
- Uma segunda planilha de preços com uma coluna de preço só, para o aviso aparecer só numa delas.
- Nenhum fake da LLM.
