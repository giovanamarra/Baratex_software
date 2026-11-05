# 23 — Catálogo em tabela em PDF e correção do mapeamento

Status: ready-for-agent
Type: task
Blocked by: 21
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Escolha do caminho: PDF com texto, mapeamento ou indicação de tabela; Tabela: vários mapeamentos)
ADRs: ADR-0006 (caminho 2), ADR-0010 (item 8: vários mapeamentos reconhecidos pelos cabeçalhos), ADR-0007 (auditoria do Perfil)
User stories: 12, 13, 17 (PDF), 22
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

PDFs em colunas passam pelo mesmo leitor de tabela, também como planilha de preços. Quando o Fornecedor muda a planilha, a gestora corrige um dos mapeamentos no Perfil, ou indica um novo, e a próxima Importação sai certa.

## Critérios de aceite

- Um PDF com texto, que não é de nenhum Layout de grade conhecido, de um Fornecedor com um mapeamento cujas colunas existem todas no PDF, é lido pelo leitor de tabela, com o caminho "tabela" (17).
- Um Fornecedor sem mapeamento que sirva: se a gestora indicar na Importação que o PDF é uma tabela, a Importação pede o mapeamento como no ticket 21, e ele é acrescentado aos outros.
- O PDF em tabela também é aceito como planilha de preços (ticket 36), com as mesmas regras.
- **Corrigir um mapeamento** do Perfil do Fornecedor muda só aquele mapeamento; os outros continuam iguais. A próxima Importação de uma planilha com aqueles cabeçalhos usa o mapeamento corrigido (12). O histórico do Perfil registra quem corrigiu, quando e qual mapeamento (13).
- **A planilha mudou** (22): quando nenhum mapeamento guardado serve (por exemplo, o cabeçalho "PREÇO" virou "VALOR"), a Importação mostra a mensagem abaixo e pede o mapeamento dessa planilha. O mapeamento novo fica guardado **junto** dos outros, sem apagar o antigo.
- Sem mapeamento que sirva e sem a indicação de tabela, o PDF continua recebendo a mensagem provisória do ticket 03, até o ticket 25 mandá-lo para a LLM.

## Erros (mensagens em português)

- Nenhum mapeamento serve (22) → `A planilha do Fornecedor Alfa mudou: nenhum mapeamento guardado serve para ela. Indique as colunas desta planilha; o mapeamento novo fica guardado junto dos outros.` (substitui `...a coluna "PREÇO" não foi encontrada. Corrija o mapeamento no Perfil do Fornecedor.`, porque agora há vários mapeamentos)
- Corrigir um mapeamento deixando-o sem preço ou sem descrição → as mensagens do ticket 21.

## O que o teste precisa

- **Catálogo fictício em tabela em PDF**, com texto, gerado no teste: cabeçalho e linhas de Ofertas inventadas.
- Uma segunda versão do mesmo Catálogo fictício com um cabeçalho renomeado.
- Um Fornecedor com dois mapeamentos, para provar que corrigir um não muda o outro.
- Nenhum fake da LLM.

## Fora deste ticket

- Foto na faixa da linha do PDF em tabela (39).
