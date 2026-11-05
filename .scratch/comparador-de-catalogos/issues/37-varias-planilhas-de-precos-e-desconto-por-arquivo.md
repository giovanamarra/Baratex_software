# 37 — Várias planilhas de preços num Catálogo e desconto por arquivo

Status: ready-for-agent
Type: task
Blocked by: 36, 32, 19
Spec: [docs/spec.md](../../../docs/spec.md) (Catálogo em mais de um arquivo › Fluxo, Código repetido entre planilhas; Modelo de dados › Preço unitário, Catálogo, Catálogos já existentes; Revisão › confirmação recusada)
ADRs: ADR-0010 (itens 3 e 9), ADR-0009 (item 3, entre planilhas), ADR-0005
User stories: 23, 110
Muda código já feito: tickets 05 (o desconto passa a ser por arquivo de onde saem as Ofertas), 06 (recusa de desconto por arquivo), 08 (a contagem soma as planilhas) e 09 (a vigência usa o desconto do arquivo da Oferta). Também muda os tickets 15, 18 e 19, que já estarão feitos: o total do Pedido e os blocos da exportação passam a usar o desconto do arquivo da linha. Esses tickets continuam resolvidos.

## O que entrega

A gestora junta num único Catálogo a planilha principal e a de promoção do mesmo Fornecedor e informa um desconto para cada uma, por exemplo 0 na de promoção e 3% na principal.

## Critérios de aceite

Várias planilhas (110)

- A Importação aceita mais de uma planilha de preços, com a confirmação abaixo antes de seguir.
- Cada planilha é lida com o seu mapeamento (o Perfil escolhe pelo cabeçalho; ticket 21). Uma planilha sem mapeamento que sirva pede um novo só para ela.
- Todas formam **um** Catálogo, com uma data só, e todas ficam guardadas como planilhas de preços.
- A contagem "Preços no arquivo" soma as planilhas.

Desconto por arquivo (23)

- A Revisão pede um desconto para **cada arquivo de onde saem Ofertas**: cada planilha, ou o arquivo do Catálogo quando não há planilha. Cada resposta é obrigatória; 0 vale.
- Cada Oferta usa o desconto do seu arquivo, na Revisão, no Catálogo, na busca, na vigência e no Pedido.
  - Exemplo: planilha de promoção com 0% e código 2001 a 10,00 → 10,00; planilha principal com 3% e código 1001 a 10,00 → 9,70.
- Migração dos Catálogos que já existem: o desconto do Catálogo passa a ser o do seu único arquivo. Nenhum Preço unitário muda.
- **Pedido:** o total da Loja (ticket 15) aplica o desconto do arquivo de cada linha; a exportação (ticket 19) faz um bloco por desconto distinto entre as linhas, agora contando o desconto do arquivo. Um Pedido com uma linha da planilha de promoção (0%) e outra da principal (3%) do mesmo Catálogo sai em dois blocos.

Código repetido entre planilhas (ADR-0009, item 3)

- O mesmo código em duas planilhas do mesmo Catálogo segue a regra do ticket 32 (agrupado na Revisão, vale o menor Preço unitário), comparando o Preço unitário **com o desconto de cada arquivo**.
  - Exemplo: código 1001 a 10,00 na promoção (0%) e a 10,20 na principal (3%, Preço unitário 9,89) → vigente a da principal, embora o preço impresso seja maior.
- Com Preço unitário igual, vale a que aparece primeiro: a ordem é a das planilhas como foram enviadas e, dentro de cada uma, a das linhas.

## Mutações que precisam morrer

| # | Mutação | Por que precisa morrer |
|---|---|---|
| M22 | Desempate do código repetido pelo **preço impresso** (sem o desconto do arquivo). | Escolheria a promoção no exemplo acima. Vinha sobrevivendo desde o ticket 09 (era a M4 da revisão, que morria só entre Catálogos). |
| M23 | Todas as Ofertas usam o desconto da **primeira** planilha. | O Preço unitário da principal sairia sem os 3%. |
| M24 | Empate de Preço unitário entre planilhas → vale a da **última** planilha enviada. | Contraria "a que aparece primeiro". |

## Erros (mensagens em português)

- Mais de uma planilha selecionada (confirmação, não erro) → `Você selecionou 2 planilhas de preços. Elas serão juntadas num único Catálogo. Deseja prosseguir com mais de um arquivo?`
- Confirmar com desconto faltando em algum arquivo (texto proposto, que estende o do ticket 06) → `Informe o desconto de cada arquivo de preços antes de confirmar. Se não houver desconto, informe 0. Falta: promocao.xlsx.`
- Desconto inválido → a mensagem do ticket 05.

## O que o teste precisa

- Duas planilhas fictícias em Excel com cabeçalhos diferentes (dois mapeamentos do mesmo Fornecedor), com um código em comum; o arquivo do Catálogo fictício do Layout A sem preço.
- Um Pedido montado pelos casos de uso com linhas das duas planilhas, e a exportação reaberta no teste (ticket 19).
- Nenhum fake da LLM.

## Fora deste ticket

- Ligar as fotos às Ofertas das planilhas (38).
- Aviso de várias colunas de preço no campo de desconto (22).
