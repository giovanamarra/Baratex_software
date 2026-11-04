---
status: accepted
---

# Pedido é exportado na planilha padrão da gestora, não no formato de cada Fornecedor

O briefing deixava fora do MVP a "geração do pedido no formato de cada fornecedor". Na prática, a gestora já envia todos os pedidos numa planilha própria, de formato fixo: um bloco por Fornecedor, as Lojas lado a lado e fórmulas de quantidade e valor. Um Representante recebe num único arquivo os pedidos de vários Fornecedores. Sem exportação, cada Pedido montado no sistema teria de ser digitado de novo nessa planilha. Decidimos que o MVP gera esse formato único; os formatos de cada Fornecedor continuam fora.

## Regras

- Um arquivo reúne um ou mais Pedidos escolhidos pela gestora, na ordem escolhida. Não existe um conceito de "envio" no sistema.
- Um Pedido pode ter Ofertas vigentes de vários Catálogos do mesmo Fornecedor. Cada Pedido gera um bloco por desconto distinto entre suas linhas. No caso comum, com um único desconto, sai um único bloco.
- Cada linha traz o código e a descrição do Fornecedor, o preço impresso por Unidade de venda **sem impostos** e a Caixa em Unidades de venda. Para cada Loja, traz a quantidade de Caixas, a quantidade de Unidades de venda e o valor.
- Quantidade, valor e somas são exportados como fórmulas, para que a gestora possa ajustar no Excel antes de enviar.
- O desconto das Condições do Catálogo aparece como linha no total do bloco e não altera o preço da linha. Por isso, linhas com descontos diferentes nunca dividem o mesmo bloco.
- Só aparecem as Lojas com alguma quantidade no Pedido.
- A observação do Pedido, em texto livre, é impressa abaixo do bloco.
- O arquivo segue a estrutura e as fórmulas da planilha da gestora, não a aparência idêntica. Subtítulos dentro do bloco e variações de cabeçalho ficam fora.

## Opções consideradas

- **Lista simples para copiar:** menos trabalho, mas mantém a digitação dupla e, com ela, o risco de a gestora abandonar o sistema.
- **Formato de cada Fornecedor:** exigiria um gerador por Fornecedor, e a gestora não precisa disso, porque todos aceitam a planilha dela.

## Consequências

Alterações feitas no Excel depois da exportação não voltam ao sistema. O histórico guarda o Pedido exportado, não necessariamente o enviado. Como o formato é fixo, um leitor dessa mesma planilha pode, no futuro, importar pedidos antigos e versões editadas.
