---
status: superseded by ADR-0006
---

# Extração de catálogos por leitor de layout, com revisão humana e sem LLM no MVP

Numa amostra de 24 arquivos reais de 8 fornecedores, todos eram PDF e a grande maioria das ofertas estava em texto selecionável, organizada em grades ou tabelas regulares. Decidimos extrair com um leitor determinístico para cada layout conhecido, sempre seguido de revisão humana. Um erro de preço que pareça plausível é o pior defeito possível neste sistema, porque leva a uma compra errada sem que ninguém perceba; por isso a extração precisa ser previsível, testável e explicável.

## Regras

- Layout não reconhecido é recusado com mensagem clara. O sistema não tenta adivinhar.
- A revisão mostra quantos preços existem no arquivo e quantas ofertas foram extraídas, e marca as linhas incompletas. Nada é salvo sem confirmação.
- Oferta avulsa pode ser digitada à mão na revisão.
- Documento sem preço não é importável, pois não há o que comparar.

## Opções consideradas

- **Leitor por layout + revisão (escolhida):** sem custo por uso e testável com TDD. Cada layout novo exige código. Um protótipo descartável encontrou de 95% a 100% das ofertas em quatro fornecedores; isso mede ofertas encontradas, não a correção de cada campo.
- **LLM para tudo + revisão:** aceita qualquer layout, mas tem custo por página, é difícil de testar, envia os catálogos a um terceiro e pode errar preços de forma plausível.
- **Leitor + LLM para layouts desconhecidos:** tem a maior cobertura, mas exige duas pipelines para explicar e testar, contra a preferência do projeto por poucas peças.

## Consequências

Um fornecedor que mude de layout, ou que mande catálogo em Excel ou foto, fica sem importação até ganhar um leitor. Uma LLM pode entrar depois como mais uma fonte de ofertas, desde que passe pela mesma revisão.
