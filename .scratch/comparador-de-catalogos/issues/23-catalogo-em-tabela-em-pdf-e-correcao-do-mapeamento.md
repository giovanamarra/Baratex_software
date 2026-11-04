# 23 — Catálogo em tabela em PDF e correção do mapeamento

Status: ready-for-agent
Type: task
Blocked by: 21
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Escolha do caminho: PDF com texto, mapeamento ou indicação de tabela)
ADRs: ADR-0006 (caminho 2), ADR-0007 (auditoria do Perfil)
User stories: 12, 13, 17 (PDF), 22

## O que entrega

PDFs em colunas passam pelo mesmo leitor de tabela. Quando o Fornecedor muda a planilha, a gestora corrige o mapeamento no Perfil, e a próxima Importação sai certa.

## Critérios de aceite

- Um PDF com texto, que não é de nenhum Layout de grade conhecido, de um Fornecedor com mapeamento no Perfil, é lido pelo leitor de tabela, com o caminho "tabela" (17).
- Um Fornecedor sem mapeamento: se a gestora indicar na Importação que o PDF é uma tabela, a Importação pede o mapeamento como no ticket 21.
- Corrigir o mapeamento do Perfil do Fornecedor faz a próxima Importação usar o mapeamento novo (12). O histórico do Perfil registra quem corrigiu e quando (13).
- Sem mapeamento e sem a indicação de tabela, o PDF continua recebendo a mensagem provisória do ticket 03, até o ticket 25 mandá-lo para a LLM.

## Erros (mensagens em português)

- O Fornecedor mudou a planilha e uma coluna do mapeamento não existe mais (22) → `A planilha do Fornecedor Alfa mudou: a coluna "PREÇO" não foi encontrada. Corrija o mapeamento no Perfil do Fornecedor.`

## O que o teste precisa

- **Catálogo fictício em tabela em PDF**, com texto, gerado no teste: cabeçalho e linhas de Ofertas inventadas.
- Uma segunda versão do mesmo Catálogo fictício com um cabeçalho renomeado.
- Nenhum fake da LLM.
