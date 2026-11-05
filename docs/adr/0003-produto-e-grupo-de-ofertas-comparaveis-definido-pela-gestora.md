---
status: accepted
---

# Produto é um grupo de Ofertas comparáveis, definido manualmente pela gestora

O briefing pedia um jeito de dizer que "esta Oferta é o mesmo produto que aquela". Nos catálogos reais não há chave comum entre fornecedores: os EANs são próprios de cada importadora e nenhum se repete, as lojas não têm sistema com código próprio, e descrições parecidas raramente indicam o mesmo item. Além disso, a gestora quer comparar itens **semelhantes**, por exemplo o mesmo utensílio em tamanhos diferentes, e não só itens idênticos. Decidimos que **Produto é um grupo de Ofertas que a gestora considera comparáveis**, e que o sistema deliberadamente não distingue "igual" de "semelhante".

## Regras

- O vínculo entre Oferta e Produto é manual: a gestora busca e liga.
- O vínculo fica guardado por Fornecedor + código do Fornecedor. Uma Oferta com o mesmo código em um Catálogo novo já chega ligada. Quando o Catálogo não traz código, o código é a descrição normalizada (ADR-0010).
- Só vira Produto o que a gestora quer acompanhar. As demais Ofertas continuam pesquisáveis, mas não entram na comparação nem no histórico por Produto.
- A comparação mostra as Ofertas do Produto lado a lado, ordenadas por Preço unitário, com descrição e foto. O sistema não elege um vencedor, porque os itens podem ser apenas semelhantes.
- O Teto de compra não pertence ao Produto: hoje é um valor único para toda mercadoria.

## Opções consideradas

- **EAN como chave:** descartada; nenhum EAN se repete entre fornecedores.
- **Código interno da loja:** descartada; não existe sistema com códigos próprios.
- **Sugestão automática por descrição ou foto:** fora do MVP. Na amostra, quase não havia pares, e um vínculo errado contamina comparação e histórico sem ninguém perceber.
- **Dois níveis (Produto idêntico dentro de um Grupo de semelhantes):** mais preciso, mas dobra o trabalho de vínculo e acrescenta um conceito que a gestora não usa.

## Consequências

Como "mais barato do Produto" pode comparar tamanhos diferentes, a tela não deve apresentar a primeira Oferta como "a melhor compra". Se um dia for preciso distinguir idênticos de semelhantes, isso exige um segundo nível e a revisão dos vínculos existentes.
