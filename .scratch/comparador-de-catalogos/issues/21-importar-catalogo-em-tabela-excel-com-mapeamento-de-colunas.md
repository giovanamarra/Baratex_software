# 21 — Importar um Catálogo em tabela Excel, com o mapeamento de colunas no Perfil do Fornecedor

Status: ready-for-agent
Type: task
Blocked by: 06, 17
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Escolha do caminho, Tabela; Casos de uso › informar mapeamento de colunas)
ADRs: ADR-0006 (caminho 2), ADR-0007 (alteração do Perfil com autor e data)
User stories: 11, 13 (mapeamento), 14 (Excel), 17 (Excel), 18, 33 (tabela)

## O que entrega

A gestora importa a planilha Excel de um Fornecedor. Na primeira vez, ela indica quais colunas são código, descrição, preço e Caixa. Nas Importações seguintes, o sistema já sabe ler a planilha.

## Critérios de aceite

- Iniciar a Importação com um .xlsx de um Fornecedor sem mapeamento faz a Importação pedir o mapeamento, mostrando os cabeçalhos encontrados (18).
- Informar o mapeamento (código, descrição, preço e Caixa, identificados pelo texto do cabeçalho) gera a Revisão com uma Oferta por linha que tem preço, com o caminho "tabela" (17).
- Linhas de título, linhas em branco e subtítulos de seção (sem código e sem preço) são ignorados.
- Uma linha com a Caixa vazia gera uma Oferta sem Caixa, que bloqueia a confirmação (ticket 06).
- Ao confirmar, o mapeamento fica guardado no Perfil do Fornecedor, com Gestor e data no histórico do Perfil (11, 13).
- A segunda Importação de .xlsx desse Fornecedor vai direto para a Revisão, sem pedir o mapeamento (11).
- Contagem (33): a Revisão mostra "Preços no arquivo: N · Ofertas extraídas: M", em que N é o número de linhas com valor na coluna de preço.
- O desconto das Condições do Catálogo é pedido como no ticket 05.
- A mensagem provisória do ticket 03 para Excel deixa de valer.

## Erros (mensagens em português)

- Mapeamento sem coluna de preço → `Indique a coluna de preço.`
- Mapeamento sem coluna de código ou de descrição → `Indique as colunas de código e de descrição.`
- Planilha sem nenhum preço numérico → `Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.`
- Arquivo .xls antigo → `Formato .xls não aceito. Abra no Excel e salve como .xlsx.`

## O que o teste precisa

- **Catálogo fictício em tabela Excel**, gerado no teste: uma linha de título, uma linha de cabeçalho, de 6 a 10 linhas de Ofertas inventadas, uma linha de subtítulo de seção e uma linha sem Caixa.
- Nenhum fake da LLM.

## Fora deste ticket

- Várias colunas de preço (22). PDF em tabela e correção do mapeamento (23).
