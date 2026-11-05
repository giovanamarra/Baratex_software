---
status: accepted
---

# Oferta vigente pelo Catálogo mais recente, com a data do Catálogo informada pela gestora

Até aqui, a data do Catálogo era o dia da Importação, e dois Catálogos do mesmo Fornecedor no mesmo dia eram desempatados pelo menor Preço unitário. A gestora pediu outra regra: uma versão atualizada do catálogo substitui a anterior, **mesmo que o preço tenha subido**. Ela também importa catálogos antigos, por exemplo o do mês anterior, que não podem derrubar o preço atual. Decidimos:

1. **Oferta vigente** é, para cada Fornecedor + código, a Oferta do Catálogo de **data do Catálogo** mais recente que tem esse código. Um código que não está no Catálogo novo continua vigente pelo Catálogo anterior: a substituição é código a código, não do Catálogo inteiro.
2. Com a **mesma data**, vale o Catálogo **confirmado por último**.
3. O **menor Preço unitário** só desempata o mesmo código repetido **dentro de um Catálogo** (inclusive entre planilhas de preços diferentes do mesmo Catálogo, ADR-0010). Com Preço unitário igual, vale a Oferta que aparece primeiro no arquivo.
4. A **data do Catálogo** é uma resposta obrigatória da gestora na Revisão, como o desconto. O campo começa vazio e tem o atalho "É de hoje", que usa o dia em que a Importação começou. Ela aceita data completa (15/10/2026) ou só mês e ano (10/2026). Para ordenar, mês e ano conta como o dia 1 daquele mês; na tela aparece como foi informado.
5. Data depois de hoje e ano antes de 2000 são recusados. Uma data anterior à do Catálogo mais recente do mesmo Fornecedor é aceita, com um aviso de que os códigos que estão nos dois continuam com o preço do mais recente.
6. A data de um Catálogo confirmado pode ser **corrigida** por qualquer Gestor, com as mesmas regras, registro de autor, data e valor anterior, e aviso de quantas Ofertas passam a ser vigentes ou deixam de ser. É o único dado do Catálogo que muda depois da confirmação.

## Opções consideradas

- **Ordem de Importação como "mais recente":** simples, mas um catálogo antigo importado depois trocaria os preços atuais por velhos, sem aviso.
- **O Catálogo novo derruba o anterior inteiro:** quebraria os Fornecedores que mandam vários Catálogos ao mesmo tempo (um por linha ou marca), e o Pedido que junta Ofertas vigentes de qualquer Catálogo do Fornecedor. Exigiria um conceito de "versão de um Catálogo" que não existe.
- **Data preenchida com o dia da Importação, sem resposta obrigatória:** menos um passo, mas esquecer de mudá-la faz um catálogo antigo virar vigente. A gestora preferiu a pergunta explícita.
- **Mês e ano empatando com qualquer dia do mês:** cria ciclos de "mais recente" entre três Catálogos e deixa a vigência indefinida.
- **Bloquear a confirmação quando há código repetido:** travaria Importações de centenas de Ofertas por repetições que costumam ser reais (o mesmo item em duas seções).

## Consequências

- Um item que o Fornecedor tirou de linha continua aparecendo como vigente, com o preço e a data do Catálogo antigo. Por isso a data do Catálogo aparece ao lado de toda Oferta em que se escolhe o que comprar (busca, comparação do Produto, inclusão no Pedido e linhas do Pedido).
- Uma Oferta que está num Pedido pode deixar de ser vigente (Catálogo novo ou data corrigida). O Pedido não muda sozinho: a linha fica marcada, com a opção de usar a Oferta vigente.
- O Catálogo passa a guardar duas datas: a data do Catálogo, que é a que vale, e o dia da Importação, só como registro.
