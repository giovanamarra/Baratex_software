Status: ready-for-agent

# Spec: Comparador de Catálogos de Fornecedores (MVP)

## Problem Statement

A gestora de compras de um grupo familiar de Lojas recebe Catálogos de muitos Fornecedores, cada um num formato diferente: PDFs em grade de cartões, tabelas em Excel ou PDF (às vezes com várias colunas de preço), catálogos de layout livre e catálogos em que código e preço existem só como imagem. Para decidir o que comprar, ela abre vários arquivos, procura itens parecidos e faz contas à mão para chegar ao Preço unitário, por exemplo para saber se um kit de 3 tesouras a R$ 9,00 sai mais barato que a tesoura avulsa de outro Fornecedor. Também confere de cabeça se o preço ainda deixa margem diante do preço único de venda das Lojas.

Depois de escolher, ela digita tudo de novo na planilha padrão de Pedido que envia aos Fornecedores e Representantes. Cada Catálogo novo substitui o anterior na prática, e ela perde a noção de como o preço de um item evoluiu. Os outros Gestores do grupo compram dos mesmos Fornecedores, mas cada um refaz esse trabalho sozinho, trocando planilhas e mensagens.

## Solution

Uma aplicação web, usada pelos Gestores do grupo, que:

1. **Importa Catálogos** de qualquer um dos formatos reais por três caminhos de extração (grade de cartões, tabela, LLM com visão), com a foto de cada Oferta quando o arquivo a traz, juntando numa só Importação o arquivo do Catálogo e as planilhas de preços que o completam. Sempre passa por uma **Revisão** em que a gestora confere, corrige e confirma as Ofertas e a data do Catálogo antes de salvar.
2. Calcula o **Preço unitário** de cada Oferta (preço impresso × (1 − desconto% das Condições do Catálogo) ÷ Conteúdo, arredondado para centavos) e destaca o que passa do **Teto de compra**.
3. Permite agrupar Ofertas comparáveis de Fornecedores diferentes num **Produto** e mostra as Ofertas vigentes desse Produto lado a lado, ordenadas por Preço unitário, com descrição e foto, sem eleger uma vencedora.
4. Guarda todos os Catálogos como histórico, para que se veja a evolução do preço de cada Produto e de cada Fornecedor.
5. Permite a cada Gestor montar **Pedidos** por Fornecedor, com a quantidade de cada Oferta para cada uma das suas Lojas, e exportá-los na planilha padrão da gestora, com fórmulas, pronta para enviar.
6. Mantém a base de compras (Fornecedores, Catálogos, Ofertas, Produtos, Teto de compra) comum ao grupo, enquanto Lojas e Pedidos pertencem a cada Gestor.

## User Stories

### Acesso e Lojas

1. Como Gestor, quero entrar no sistema com usuário e senha, para que só pessoas do grupo vejam a base de compras.
2. Como Gestor, quero ver as minhas Lojas assim que entro, para saber para quais Lojas estou comprando.
3. Como Gestor, quero que só eu possa editar as minhas Lojas, para que outro Gestor não altere meus dados por engano.
4. Como Gestor, quero que só eu possa criar e editar os meus Pedidos, para que meu trabalho de compra não seja alterado por outra pessoa.
5. Como Gestor, quero que um Pedido só aceite Lojas que são minhas, para que eu não destine mercadoria a uma Loja de outro Gestor.
6. Como responsável pela instalação, quero cadastrar Gestores e as Lojas de cada um sem tela própria de autocadastro, para que só o grupo tenha acesso.
7. Como Gestor, quero sair do sistema, para que outra pessoa no mesmo computador não use minha sessão.

### Fornecedores e Perfil do Fornecedor

8. Como Gestor, quero cadastrar um Fornecedor pelo nome, para poder associar Catálogos a ele sem depender do nome do arquivo ou da marca.
9. Como Gestor, quero escolher o Fornecedor ao iniciar uma Importação, para que o Catálogo fique ligado à empresa certa mesmo quando o arquivo traz o nome de uma marca.
10. Como Gestor, quero registrar no Perfil do Fornecedor se ele permite Fracionamento e qual a menor quantidade aceita, para que os Pedidos respeitem a compra mínima.
11. Como Gestor, quero que o mapeamento de colunas de cada formato de planilha do Fornecedor (código, descrição, preço, Caixa) fique guardado no Perfil do Fornecedor e seja reconhecido pelos cabeçalhos, para não precisar indicá-lo de novo a cada Importação, mesmo quando ele alterna entre planilhas diferentes.
12. Como Gestor, quero corrigir o mapeamento de colunas do Perfil do Fornecedor quando ele mudar a planilha, para que a próxima Importação saia certa.
13. Como Gestor, quero ver quem alterou o Perfil do Fornecedor e quando, para entender por que uma comparação mudou.

### Importação: envio e escolha do caminho

14. Como Gestor, quero enviar o arquivo do Catálogo de preferência em PDF, mas também em planilha Excel ou imagem, com um aviso quando não é PDF, para que todos os formatos que recebo possam entrar no sistema sem que eu esqueça o arquivo com as fotos.
15. Como Gestor, quero informar na Revisão de quando é o Catálogo (data completa ou só mês e ano), com o dia da Importação a um clique, para que um catálogo do mês anterior importado hoje não passe na frente do atual.
16. Como Gestor, quero que o sistema reconheça sozinho quando um PDF é uma grade de cartões de um Layout conhecido, para não ter que escolher o leitor.
17. Como Gestor, quero que Excel e PDFs em tabela sejam lidos por um leitor de tabela, para que Catálogos em colunas entrem sem LLM.
18. Como Gestor, na primeira Importação de um formato de planilha de um Fornecedor, quero indicar quais colunas são código (se houver), descrição (uma ou mais colunas, em ordem), preço e Caixa, para que o sistema saiba ler aquela planilha.
19. Como Gestor, quero que, num Catálogo com várias colunas de preço, valha a menor de cada linha, para comparar sempre o melhor preço que o Fornecedor oferece.
20. Como Gestor, quero que Catálogos de layout livre ou só em imagem sejam lidos por uma LLM com visão, para não ter que digitar dezenas de páginas.
21. Como Gestor, quando o arquivo do Catálogo tem produtos mas nenhum preço, quero que o sistema perceba e exija as planilhas de preços, para não perder as fotos de um Fornecedor que manda fotos e preços separados nem criar um Catálogo sem preço.
22. Como Gestor, quando a leitura falhar, quero uma mensagem que diga o que aconteceu e o que posso fazer, para não ficar sem saber se o Catálogo entrou.

### Importação: Condições do Catálogo

23. Como Gestor, quero informar o desconto além do impresso a cada Importação, um para cada arquivo de onde saem as Ofertas, para que o Preço unitário reflita a negociação de cada planilha, por exemplo 0 na de promoção e 3% na principal.
24. ~~Como Gestor, quero que a Importação não peça desconto em Catálogos com várias colunas de preço~~ (removida pelo ADR-0010: o desconto é sempre perguntado). Como Gestor, num arquivo com várias colunas de preço, quero ser avisado de que a menor coluna pode já ter desconto, para não aplicar o desconto duas vezes.
25. Como Gestor, quero que um desconto já impresso no Catálogo não seja aplicado de novo, para que o Preço unitário não fique artificialmente baixo.

### Revisão

26. Como Gestor, quero ver todas as Ofertas extraídas numa tela de Revisão antes de salvar, para que nada errado entre na base sem eu ver.
27. Como Gestor, quero ver em cada Oferta de qual caminho de extração ela veio, para saber quanto confiar nela.
28. Como Gestor, quero ver cada Oferta lida pela LLM ao lado da imagem da página de origem, para conferir o preço com o original.
29. Como Gestor, quero que não seja possível confirmar em lote as Ofertas lidas pela LLM sem passar pelas páginas, para que um preço errado mas plausível não passe despercebido.
30. Como Gestor, quero que Ofertas com preço ausente, zero ou muito fora do padrão do próprio Catálogo fiquem marcadas, para corrigi-las antes de salvar.
31. Como Gestor, quero que uma Oferta sem Caixa não possa ser confirmada até eu informar a Caixa, para que todo Pedido tenha a compra mínima definida.
32. Como Gestor, quero que Ofertas com Unidade de venda ambígua, como um kit vendido em set, fiquem marcadas, para eu conferir o que o preço compra.
33. Como Gestor, quero ver quantos preços havia no arquivo e quantas Ofertas foram extraídas, quando o caminho permitir, para perceber se alguma ficou de fora.
34. Como Gestor, quero corrigir código, descrição, preço, Caixa, Embalagem intermediária e foto de qualquer Oferta na Revisão, para consertar erros de leitura.
35. Como Gestor, quero adicionar uma Oferta à mão na Revisão, para incluir um item que a extração não encontrou.
36. Como Gestor, quero remover uma Oferta na Revisão, para descartar lixo de leitura ou itens que não me interessam.
37. Como Gestor, quero ver o Preço unitário de cada Oferta já na Revisão, para perceber na hora um preço absurdo.
38. Como Gestor, quero confirmar a Revisão e só então ter o Catálogo salvo, para que uma Importação abandonada não deixe dados pela metade.
39. Como Gestor, quero poder abandonar uma Revisão sem salvar nada, para recomeçar a Importação se algo saiu muito errado.
40. Como Gestor, quero que uma Oferta com código já ligado a um Produto chegue ligada a ele num Catálogo novo do mesmo Fornecedor, para não refazer vínculos a cada Importação.
41. Como Gestor, quero que uma Oferta com código que já tem Conteúdo definido chegue com esse Conteúdo, para não repetir a mesma decisão.

### Conteúdo e Preço unitário

42. Como Gestor, quero que o Conteúdo de toda Oferta comece em 1, para que o pior erro possível seja um kit parecer caro, nunca barato.
43. Como Gestor, quero que o sistema sugira mudar o Conteúdo quando a descrição citar peças, para eu decidir se o kit é vendido separado.
44. Como Gestor, quero definir o Conteúdo de uma Oferta, para que o Preço unitário reflita quantos itens a Loja vende a partir de uma Unidade de venda.
45. Como Gestor, quero que a decisão de Conteúdo fique guardada por Fornecedor e código, para valer também nos próximos Catálogos.
46. Como Gestor, quero ver quem alterou o Conteúdo e quando, para entender por que um Preço unitário mudou.
47. Como Gestor, quero que Caixa e Embalagem intermediária nunca dividam o preço, para que o Preço unitário não fique dezenas de vezes menor que o real.
48. Como Gestor, quero que o Preço unitário ignore impostos, para comparar a mercadoria como eu seleciono, deixando a parte fiscal com a contabilidade.

### Teto de compra

49. Como Gestor, quero definir um Teto de compra único para toda mercadoria, para que o sistema saiba o maior Preço unitário que ainda dá lucro.
50. Como Gestor, quero que toda Oferta com Preço unitário acima do Teto de compra apareça destacada, em qualquer lista, para não comprar sem margem.
51. Como Gestor, quero mudar o Teto de compra quando o preço único de venda das Lojas mudar, para que o destaque continue correto.

### Ofertas vigentes e busca

52. Como Gestor, quero buscar Ofertas por código ou descrição em todos os Catálogos, para achar rapidamente um item que vi num arquivo.
53. Como Gestor, quero que a busca mostre só as Ofertas vigentes por padrão, para não comparar preços antigos.
54. Como Gestor, quero que a Oferta vigente seja a do Catálogo de data mais recente do Fornecedor que tem aquele código, mesmo que o preço tenha subido, para que uma versão atualizada do catálogo substitua a anterior.
55. Como Gestor, quero que, com dois Catálogos do mesmo Fornecedor com a mesma data, valha o confirmado por último, e que o menor preço só desempate o mesmo código repetido dentro de um Catálogo, para que a versão mais nova sempre ganhe.
56. Como Gestor, quero filtrar a busca por Fornecedor, para olhar um Fornecedor de cada vez.
57. Como Gestor, quero ver nos resultados da busca o Preço unitário, a Caixa, o Fornecedor, a data do Catálogo e a foto quando houver, para avaliar sem abrir o arquivo e saber se o preço ainda serve para um Pedido.
58. Como Gestor, quero ver os Catálogos importados de cada Fornecedor, com a data do Catálogo e o dia da Importação, para saber o que já entrou no sistema.

### Produtos e comparação

59. Como Gestor, quero criar um Produto com o nome que eu escolher, para agrupar Ofertas que considero comparáveis.
60. Como Gestor, quero ligar uma Oferta a um Produto a partir da busca, para montar a comparação aos poucos.
61. Como Gestor, quero ligar Ofertas de Fornecedores diferentes ao mesmo Produto, mesmo que sejam apenas semelhantes, como tamanhos diferentes do mesmo utensílio.
62. Como Gestor, quero desligar uma Oferta de um Produto, para corrigir um vínculo errado.
63. Como Gestor, quero que o vínculo fique guardado por Fornecedor e código, para que valha para os Catálogos futuros desse Fornecedor.
64. Como Gestor, quero ver quem ligou ou desligou uma Oferta de um Produto e quando, para entender mudanças na comparação.
65. Como Gestor, quero ver as Ofertas vigentes de um Produto lado a lado, ordenadas por Preço unitário, com descrição, foto, Fornecedor, Caixa e data do Catálogo, para escolher o que comprar.
66. Como Gestor, quero que a comparação não indique uma "melhor compra", porque os itens podem ser só semelhantes e a decisão é minha.
67. Como Gestor, quero ver na comparação, lado a lado, um kit e um item avulso do mesmo Fornecedor ou de outro, cada um com seu Preço unitário, para saber qual sai mais barato por item.
68. Como Gestor, quero renomear e listar meus Produtos, para manter a lista organizada.
69. Como Gestor, quero que Ofertas sem Produto continuem pesquisáveis, para não ter que ligar tudo o que importo.

### Histórico de preço

70. Como Gestor, quero que cada Catálogo novo seja guardado sem apagar os anteriores, para manter a série histórica de preços.
71. Como Gestor, quero ver a evolução do Preço unitário de um Produto ao longo do tempo, por Fornecedor, para saber se um preço subiu ou caiu.
72. Como Gestor, quero ver o histórico de preço de uma Oferta (Fornecedor + código) mesmo sem Produto, para checar um item específico.
73. Como Gestor, quero comparar os Fornecedores de um Produto ao longo do tempo, para saber quem costuma ser mais barato.

### Pedidos

74. Como Gestor, quero criar um Pedido para um Fornecedor, para organizar minha compra com ele.
75. Como Gestor, quero adicionar ao Pedido Ofertas vigentes de qualquer Catálogo desse Fornecedor, para comprar de vários Catálogos dele num Pedido só.
76. Como Gestor, quero adicionar ao Pedido uma Oferta direto da comparação de um Produto, para ir da decisão à compra sem buscar de novo.
77. Como Gestor, quero informar, para cada Oferta do Pedido, a quantidade de Caixas para cada uma das minhas Lojas, para dividir a compra entre elas.
78. Como Gestor, quando o Fornecedor permite Fracionamento, quero informar uma quantidade menor que a Caixa, para comprar só o necessário, respeitando o mínimo do Perfil do Fornecedor.
79. Como Gestor, quero ser impedido de informar menos que uma Caixa quando o Fornecedor não permite Fracionamento, para não montar um Pedido que ele vai recusar.
80. Como Gestor, quero ver no Pedido, por Loja, a quantidade em Unidades de venda e o valor, para conferir o total antes de exportar.
81. Como Gestor, quero escrever uma observação de texto livre no Pedido, para passar instruções ao Fornecedor.
82. Como Gestor, quero editar e remover linhas de um Pedido, para ajustar a compra.
83. Como Gestor, quero listar meus Pedidos com Fornecedor e data, para retomar um Pedido em andamento.
84. Como Gestor, quero ver Ofertas acima do Teto de compra destacadas também no Pedido, para não deixar passar uma compra sem margem.

### Exportação de Pedidos

85. Como Gestor, quero escolher um ou mais Pedidos e a ordem deles e exportá-los num único arquivo de planilha, para enviar tudo de uma vez a um Representante.
86. Como Gestor, quero que a planilha siga a estrutura e as fórmulas da minha planilha padrão, para que Fornecedores e Representantes recebam o que já conhecem.
87. Como Gestor, quero que cada Pedido vire um bloco por desconto distinto entre suas linhas, para que o desconto fique certo em cada bloco.
88. Como Gestor, quero que cada linha traga código (vazio quando o Catálogo não tem código) e descrição do Fornecedor, preço impresso por Unidade de venda sem impostos e Caixa em Unidades de venda, para o Fornecedor reconhecer o item.
89. Como Gestor, quero que cada linha traga, por Loja, a quantidade de Caixas, a quantidade de Unidades de venda e o valor, para o Fornecedor separar a entrega por Loja.
90. Como Gestor, quero que quantidades, valores e somas saiam como fórmulas, para poder ajustar no Excel antes de enviar.
91. Como Gestor, quero que o desconto das Condições do Catálogo apareça como linha no total do bloco, sem alterar o preço da linha, como na minha planilha.
92. Como Gestor, quero que só apareçam as Lojas com alguma quantidade no Pedido, para a planilha não ficar cheia de colunas vazias.
93. Como Gestor, quero que a observação do Pedido saia abaixo do bloco, para o Fornecedor lê-la junto com o Pedido.
94. Como Gestor, quero que o sistema registre a data de cada exportação de um Pedido, para o histórico mostrar quando ele saiu.

### Painéis por Loja

95. Como Gestor, quero ver, para cada uma das minhas Lojas, o volume dos meus Pedidos por Fornecedor e por período, para entender quanto compro para cada Loja.
96. Como Gestor, quero que o painel diga claramente que mostra Pedidos de compra, e não vendas, para não tirar conclusões erradas sobre o que cada Loja vende.
97. Como Gestor, quero ver nos painéis a evolução de preço dos Produtos que acompanho e a comparação entre Fornecedores, para decidir compras futuras.

### Base comum do grupo

98. Como Gestor, quero ver os mesmos Fornecedores, Catálogos, Ofertas e Produtos que os outros Gestores, para não importar o mesmo arquivo várias vezes.
99. Como Gestor, quero que um Catálogo importado por outro Gestor já sirva para as minhas comparações e Pedidos, para aproveitar o trabalho do grupo.
100. Como Gestor, quero que meus Pedidos não apareçam para os outros Gestores no MVP, para manter minha compra privada até que essa consulta seja desenhada.

### Data do Catálogo e vigência (ADR-0009)

101. Como Gestor, quero que a Revisão não seja confirmada sem a data do Catálogo, para que nenhum catálogo antigo vire vigente por esquecimento.
102. Como Gestor, quero que uma data depois de hoje ou com ano antes de 2000 seja recusada, para não deixar um erro de digitação vigente por anos.
103. Como Gestor, quero ser avisado quando a data informada é anterior à do Catálogo mais recente do mesmo Fornecedor, para saber que os códigos que estão nos dois continuam com o preço do mais recente.
104. Como Gestor, quero corrigir a data de um Catálogo já confirmado, vendo antes quantas Ofertas passam a ser vigentes ou deixam de ser, para consertar uma data errada sem refazer a Importação.
105. Como Gestor, quero ver quem corrigiu a data de um Catálogo e quando, para entender por que uma Oferta vigente mudou.
106. Como Gestor, quero que as Ofertas com o mesmo código no mesmo Catálogo apareçam agrupadas na Revisão, lado a lado, para remover as erradas; se eu não remover, quero que valha a de menor Preço unitário.
107. Como Gestor, quero ver a data do Catálogo ao lado de toda Oferta que posso pôr num Pedido (busca, comparação do Produto, inclusão e linhas do Pedido), para saber se o preço ainda serve.
108. Como Gestor, quando uma Oferta do meu Pedido deixa de ser vigente, quero ver o preço mais recente desse código e poder trocar a linha pela Oferta vigente, sem que o sistema troque sozinho, para decidir se aceito o preço novo.

### Catálogo em mais de um arquivo (ADR-0010)

109. Como Gestor, depois de enviar o arquivo do Catálogo, quero sempre poder enviar planilhas de preços ou pular, para completar o Catálogo quando o Fornecedor manda os preços à parte.
110. Como Gestor, quero enviar mais de uma planilha de preços na mesma Importação, com uma confirmação, para juntar a planilha principal e a de promoção do mesmo Fornecedor num único Catálogo.
111. Como Gestor, quero que, quando houver planilhas de preços, as Ofertas saiam delas e a foto venha do arquivo do Catálogo, ligada pelo código ou, sem código, pela descrição igual e única (dentro da marca da página quando houver), para não ligar a foto de um item a outro.
112. Como Gestor, quero que a Oferta com preço diferente no arquivo do Catálogo e na planilha fique marcada, para conferir qual vale.
113. Como Gestor, quero ver na Revisão as fotos do arquivo do Catálogo que não acharam Oferta e ligá-las à mão a uma Oferta sem foto, para aproveitar as fotos que a descrição não ligou.
114. Como Gestor, quero que uma planilha sem coluna de código seja aceita, com a descrição completa fazendo o papel de código, para importar Fornecedores que não usam código.
115. Como Gestor, quero ver o arquivo do Catálogo e as planilhas de preços de cada Catálogo, com o papel de cada um, para conferir o original.

### Fotos (ADR-0011)

116. Como Gestor, quero que a foto seja importada em qualquer caminho (grade de cartões, tabela em Excel ou PDF, LLM) sempre que o arquivo do Catálogo a trouxer, para reconhecer o produto sem abrir o arquivo.
117. Como Gestor, quero conferir as fotos recortadas pela LLM junto com as páginas, e trocar ou tirar uma foto na Revisão, para que uma foto errada não entre na base.
118. Como Gestor, quero que uma Oferta sem foto mostre a foto mais recente do mesmo código vinda de um Catálogo anterior, com a data desse Catálogo, para reconhecer o item mesmo quando o Fornecedor só mandou a planilha.

## Implementation Decisions

### Arquitetura e tecnologia

- **Monólito web em Python com Django**, HTML renderizado no servidor e **SQLite**. Django foi escolhido porque já traz login, sessões, ORM, migrações, painel administrativo e cliente de teste: menos peças para montar e explicar. PostgreSQL só entra se for preciso; o código não deve depender de recursos exclusivos do SQLite.
- Cadastro de Gestores e Lojas é feito pelo painel administrativo do Django, sem tela de autocadastro.
- O MVP é dividido em módulos com responsabilidades distintas, cada um com uma interface pequena de casos de uso. As telas web são finas e só chamam esses casos de uso:
  - **Contas**: Gestor, Loja, autenticação e as regras de autorização (Lojas e Pedidos pertencem a um Gestor).
  - **Catálogos**: Fornecedor, Perfil do Fornecedor, Catálogo, Oferta, Condições do Catálogo, cálculo do Preço unitário, Oferta vigente, Teto de compra, busca e histórico de preço.
  - **Extração**: transforma um arquivo enviado numa proposta de Ofertas por um dos três caminhos. Não grava nada; devolve Ofertas propostas, com o caminho de origem, a página de origem (quando houver) e as marcas de conferência.
  - **Importação e Revisão**: guarda a Revisão em andamento, aplica correções da gestora, valida as regras de confirmação e, ao confirmar, cria o Catálogo e suas Ofertas de uma vez só (transação única).
  - **Produtos**: Produto, vínculo entre Oferta e Produto, comparação.
  - **Pedidos**: Pedido, linhas, quantidades por Loja, validação de Caixa e Fracionamento, observação e exportação para planilha.
  - **Painéis**: consultas de leitura sobre Ofertas, Produtos e Pedidos.

### Casos de uso (interface do seam principal)

Funções de aplicação, chamadas pelas telas e pelos testes. Toda função que altera dados recebe o Gestor que age, para autorização e auditoria. Nomes indicativos:

- Importação: iniciar Importação (Fornecedor, arquivo do Catálogo) → Revisão em andamento; enviar planilhas de preços ou pular; informar mapeamento de colunas; informar Condições do Catálogo (desconto por arquivo de preços); informar a data do Catálogo; corrigir, adicionar e remover Oferta proposta; ligar, trocar e tirar a foto de uma Oferta proposta; marcar página da LLM como conferida; confirmar Revisão → Catálogo; abandonar Revisão.
- Catálogos: definir Perfil do Fornecedor (com vários mapeamentos); definir Conteúdo (Fornecedor + código); definir Teto de compra; corrigir a data do Catálogo; buscar Ofertas (texto, Fornecedor, só vigentes); histórico de preço de uma Oferta.
- Produtos: criar e renomear Produto; ligar e desligar Oferta; comparar Produto → Ofertas vigentes ordenadas por Preço unitário; evolução de preço do Produto por Fornecedor.
- Pedidos: criar Pedido (Fornecedor); adicionar, alterar e remover linha; definir quantidade por Loja; definir observação; exportar Pedidos (lista ordenada) → arquivo de planilha.
- Painéis: volume de Pedidos por Loja, Fornecedor e período.

Erros de regra de negócio são exceções de domínio com mensagem em português que a tela mostra à gestora (por exemplo: Oferta sem Caixa, quantidade abaixo do mínimo, Loja de outro Gestor, arquivo sem preço e sem planilha de preços, data do Catálogo ausente ou futura). Nunca falham em silêncio.

### Modelo de dados (decisões)

- **Oferta** guarda separadamente: código do Fornecedor (opcional), descrição, preço impresso, Caixa, Embalagem intermediária (opcional), foto (opcional), caminho de extração, arquivo de origem e página de origem, e a posição no arquivo (para o desempate do código repetido). O Preço unitário é **derivado**, nunca digitado.
- **Código** (chave de Conteúdo, vínculo de Produto, vigência e histórico): o código do Fornecedor ou, quando a Oferta não tem código, a descrição normalizada (sem acento, sem maiúsculas e sem espaços duplicados). As duas formas nunca se misturam: uma Oferta sem código nunca casa com uma que tem (ADR-0010).
- **Preço unitário = preço impresso × (1 − desconto%) ÷ Conteúdo**, arredondado para centavos (meio centavo para cima); o desconto é o do arquivo de preços de onde a Oferta veio (ADR-0005, ADR-0010). Impostos são ignorados; a alíquota impressa não é guardada nem exibida.
- **Conteúdo** é guardado por Fornecedor + código, e não por Oferta, para valer em Catálogos futuros. O padrão é 1.
- **Vínculo Oferta → Produto** é guardado por Fornecedor + código (ADR-0003).
- **Catálogo** guarda Fornecedor, **data do Catálogo** (ano, mês e dia opcional, informada pela gestora; ADR-0009), **dia da Importação** (só registro), Gestor que importou, **arquivos de origem** (um arquivo do Catálogo e zero ou mais planilhas de preços, cada um com o papel e, se for de onde saem Ofertas, o seu desconto) e Condições do Catálogo (desconto percentual por arquivo de preços, informado obrigatoriamente; 0 quando não houver desconto). Catálogos nunca são sobrescritos; só a data do Catálogo pode ser corrigida depois de confirmada.
- **Catálogos já existentes** (antes do ADR-0009): a data do Catálogo é a data completa igual ao dia da Importação, e o desconto do Catálogo passa a ser o do seu único arquivo.
- **Oferta vigente** é calculada, não armazenada: para cada Fornecedor + código, a Oferta do Catálogo de data do Catálogo mais recente (só mês e ano conta como o dia 1); mesma data → o Catálogo confirmado por último; o mesmo código repetido no mesmo Catálogo → a de menor Preço unitário, e com Preço unitário igual a que aparece primeiro no arquivo (ADR-0009).
- **Foto** é um arquivo na pasta de arquivos (`fotos/`), reduzido (lado maior até 600 px, JPEG) e nomeado pela impressão digital do conteúdo, para não guardar a mesma foto duas vezes; a Oferta guarda só a referência. A foto mostrada numa Oferta sem foto, vinda de Catálogo anterior, é calculada na exibição e não é gravada (ADR-0011).
- **Teto de compra** é um único valor do grupo.
- **Perfil do Fornecedor**: Fracionamento (sim/não e menor quantidade, em Unidades de venda) e uma lista de mapeamentos de colunas, cada um reconhecido pelos cabeçalhos: código (opcional), descrição (uma ou mais colunas, em ordem), preço (uma ou mais colunas) e Caixa.
- **Auditoria**: mudanças em Perfil do Fornecedor, vínculo Oferta → Produto, Conteúdo e data do Catálogo guardam autor e data (ADR-0007, ADR-0009). Basta um registro simples de alterações; não é preciso desfazer.
- **Pedido** pertence a um Gestor e a um Fornecedor; tem observação e as datas de criação e de cada exportação. Cada linha aponta para uma Oferta (de qualquer Catálogo do Fornecedor) e tem uma quantidade por Loja. A linha nunca troca de Oferta sozinha: quando a Oferta deixa de ser vigente, a linha fica marcada com o preço vigente e a opção de trocar. A quantidade é guardada em Unidades de venda; a tela pede Caixas, e só aceita valor fracionado quando o Perfil do Fornecedor permite Fracionamento e a quantidade respeita o mínimo.
- Fornecedor, Perfil, Catálogo, Oferta, Produto e Teto pertencem ao grupo; Loja e Pedido pertencem a um Gestor (ADR-0007).

### Extração

- Interface única do módulo: arquivo + Fornecedor (+ Perfil) → lista de Ofertas propostas, cada uma com foto quando houver + metadados (caminho, contagem de preços encontrados no arquivo quando disponível, páginas renderizadas para a conferência da LLM, marca da página quando houver). A Importação chama a Extração uma vez para o arquivo do Catálogo e uma vez para cada planilha de preços, e junta os resultados (ver "Catálogo em mais de um arquivo").
- **Escolha do caminho**: Excel → tabela. PDF com texto → tenta reconhecer um Layout de grade de cartões pelo conteúdo; se não reconhecer e houver mapeamento de tabela no Perfil (ou a gestora indicar que é tabela), usa o leitor de tabela; senão, LLM. PDF sem texto selecionável ou imagem → LLM.
- **Grade de cartões**: um leitor determinístico por Layout conhecido, cada um com uma função de reconhecimento pelo conteúdo. Layouts novos são acrescentados como novos leitores, sem mexer nos outros.
- **Tabela**: um único leitor genérico guiado por um dos mapeamentos do Perfil do Fornecedor: vale o mapeamento cujas colunas existem todas nos cabeçalhos; se nenhum servir, a gestora indica um novo, que é acrescentado ao Perfil. Código é opcional; a descrição pode juntar várias colunas, em ordem. Só as colunas marcadas como preço contam (uma coluna de preço sugerido de venda, por exemplo, não é marcada). Com várias colunas de preço, usa a menor de cada linha; o desconto continua sendo perguntado, com o aviso de que a menor coluna pode já ter desconto.
- **LLM com visão**: adaptador para **Claude Haiku** (Haiku 5.5 na data desta spec), atrás de uma interface trocável "ler página → Ofertas propostas". O modelo e a chave de API vêm da configuração, nunca do código. A resposta é pedida em formato estruturado e validada; resposta inválida vira erro claro na Revisão, nunca Oferta silenciosa. Cada Oferta lida pela LLM guarda a página de origem. A resposta inclui, para cada item, a área da foto na página (quando houver) e a marca indicada na página (quando houver), e o preço pode vir ausente.
- **Marcas de conferência** calculadas na extração ou na Revisão: preço ausente ou zero; preço muito fora do padrão do próprio Catálogo; Caixa ausente (bloqueia a confirmação); Unidade de venda ambígua; sugestão de Conteúdo quando a descrição cita peças; **código repetido** no mesmo Catálogo (não bloqueia; ADR-0009); **preço diferente no Catálogo** (não bloqueia; ADR-0010).
- **Catálogo sem preço**: a leitura do arquivo do Catálogo achou produtos (código ou descrição) e nenhum preço. A Importação exige planilhas de preços, sem a opção de pular: `Este arquivo não tem preços. Envie a planilha de preços para continuar.` Arquivo que não abre e leitura sem nenhum produto continuam sendo erros de Importação. Alguns produtos sem preço não é Catálogo sem preço: é Revisão normal, com a Oferta sem preço bloqueando.
- **Foto**: capturada em todos os caminhos quando o arquivo do Catálogo traz a imagem do item: imagem do cartão (grade), imagem ancorada na linha (Excel), imagem na faixa da linha (PDF em tabela), recorte da área devolvida pela LLM. Item sem imagem → Oferta sem foto, sem marca. Planilhas de preços não dão foto (ADR-0011).

### Catálogo em mais de um arquivo (ADR-0010)

- **Fluxo**: enviar o arquivo do Catálogo (aviso quando não é PDF: `O arquivo enviado não é um PDF. O Catálogo costuma vir em PDF, com as fotos; a planilha de preços, quando houver, é pedida depois. Deseja prosseguir com este arquivo?`) → ler → `Tem uma planilha de preços para completar este Catálogo?` [Enviar planilha] [Pular] → (mais de uma planilha: `Você selecionou 2 planilhas de preços. Elas serão juntadas num único Catálogo. Deseja prosseguir com mais de um arquivo?`) → mapeamento de cada planilha, se preciso → Revisão única.
- **Planilha de preços**: .xlsx ou PDF em tabela, lida pelo leitor de tabela. A contagem "Preços no arquivo" passa a somar as planilhas.
- **De onde saem as Ofertas**: sem planilha, do arquivo do Catálogo (como antes). Com planilhas, só delas; o arquivo do Catálogo dá a foto e, se tiver preço diferente, a marca "preço diferente no Catálogo: R$ X,XX".
- **Ligação da foto**: (1) pelo código, quando as duas fontes têm código; (2) senão, pela descrição normalizada igual e única nas duas fontes, dentro da marca da página quando o arquivo do Catálogo indicar uma; (3) nunca por semelhança aproximada.
- **Só numa fonte**: Oferta sem foto ligada → Oferta normal sem foto, com o resumo `Fotos ligadas: 46 de 77 Ofertas.`; foto sem Oferta → seção "Fotos do catálogo sem preço na planilha (N)", com a foto e a descrição lida, de onde a gestora liga a foto a uma Oferta sem foto. Fotos não ligadas são descartadas ao confirmar. Nada disso bloqueia.
- **Código repetido entre planilhas** segue a regra do código repetido no mesmo Catálogo (ADR-0009), comparando o Preço unitário com o desconto de cada arquivo.

### Revisão

- A Revisão em andamento é persistida (rascunho), para sobreviver a uma navegação ou a um recarregamento, mas não cria Catálogo nem Oferta até a confirmação.
- A confirmação é recusada enquanto houver: Oferta sem Caixa; Oferta sem preço válido; desconto não informado em algum arquivo de onde saem Ofertas (informar 0 vale como resposta; sem exceção para várias colunas de preço); data do Catálogo não informada (`Informe de quando é este Catálogo antes de confirmar.`); página lida pela LLM não marcada como conferida pela gestora.
- **Data do Catálogo** (ADR-0009): campo vazio, com o atalho `É de hoje (dd/mm/aaaa)` (dia em que a Importação começou). Aceita `15/10/2026`, `10/2026` e `15/10/26` (ano com 2 dígitos = 20xx); outro formato → `Informe a data do Catálogo como dia/mês/ano ou mês/ano, por exemplo 15/10/2026 ou 10/2026.` Depois de hoje → `A data do Catálogo não pode ser depois de hoje.`; ano antes de 2000 → `Confira o ano da data do Catálogo.` Anterior ao Catálogo mais recente do Fornecedor → aviso, sem bloquear: `Este Catálogo é mais antigo que o de 15/10/2026 deste Fornecedor: os códigos que estão nos dois continuam com o preço do mais recente.` Fica no rascunho e pode ser trocada até confirmar.
- **Código repetido**: as Ofertas do mesmo código aparecem agrupadas ("Código repetido (N Ofertas)"), lado a lado, com descrição, preço, Caixa, página de origem e foto; a gestora remove as erradas. Não bloqueia.
- **Fotos**: a Revisão mostra a foto de cada Oferta proposta; a gestora pode trocar, tirar ou ligar uma foto (ver "Catálogo em mais de um arquivo"). Fotos recortadas pela LLM são conferidas com as páginas.
- A confirmação aplica, para cada Oferta, o Conteúdo e o vínculo de Produto já guardados por Fornecedor + código.
- **Corrigir a data** de um Catálogo confirmado: pela página do Catálogo, por qualquer Gestor, com as mesmas regras, aviso antes de salvar (`Com a nova data, 37 Ofertas deste Catálogo deixam de ser vigentes.`) e registro de autor, data e valor anterior.

### Exportação

- Gera um arquivo Excel com fórmulas reais (quantidade, valor e somas), seguindo a estrutura da planilha padrão da gestora (ADR-0004): um bloco por Pedido e desconto distinto; Lojas lado a lado, só as que têm quantidade; desconto como linha no total do bloco; observação abaixo do bloco. Reproduz a estrutura e as fórmulas, não a aparência idêntica.
- A exportação registra a data no Pedido; o Pedido continua editável. Não existe conceito de "envio".

### Painéis

- Volume de Pedidos (em valor e em Caixas) por Loja do Gestor, por Fornecedor e por mês, com rótulo explícito de "Pedidos de compra".
- Evolução do Preço unitário por Produto e Fornecedor, a partir das Ofertas de todos os Catálogos.

## Testing Decisions

- **O que é um bom teste aqui**: verifica comportamento externo pelos casos de uso, como "importar este Catálogo fictício, confirmar a Revisão, buscar e ver o Preço unitário X", e nunca detalhes internos, como qual método foi chamado ou como uma tabela está organizada. Se a implementação for reescrita sem mudar o comportamento, os testes continuam passando.
- **Seam principal: a camada de casos de uso**, com banco SQLite real (o banco de teste do Django) e sem mocks internos. A maior parte dos testes entra por aí: regras de Preço unitário, Oferta vigente, Teto de compra, regras de confirmação da Revisão, vínculos de Produto, Caixa e Fracionamento, e a exportação.
- **Um único fake na fronteira externa: a LLM com visão.** Os testes usam uma implementação falsa da interface "ler página → Ofertas propostas", com respostas fixas, inclusive respostas inválidas e preços errados plausíveis. Nenhum teste chama a API real (ADR-0006).
- **Poucos testes pelo cliente HTTP do Django**, para login obrigatório e autorização: um Gestor não edita Loja nem Pedido de outro, e não inclui Loja de outro num Pedido.
- Além dos testes de autorização, cada tela principal tem um teste de que abre e mostra o essencial, para pegar template quebrado.
- **Catálogos fictícios**: cada Layout de grade de cartões e o leitor de tabela são testados com arquivos fictícios gerados no próprio teste ou guardados como fixtures, imitando a estrutura dos reais sem copiar dados. Catálogos e pedidos reais nunca entram no repositório (já ignorados pelo controle de versão).
- **Exportação**: o teste exporta Pedidos, reabre a planilha gerada e verifica blocos, Lojas presentes, valores calculados e a presença das fórmulas (não só dos valores).
- **Módulos testados**: Catálogos (Preço unitário, Oferta vigente, Teto, histórico), Extração (via Importação, com arquivos fictícios e LLM falsa), Importação e Revisão, Produtos, Pedidos (incluindo exportação), Contas (autorização). Painéis têm testes das consultas de volume e evolução pelo mesmo seam.
- **Desenvolvimento por TDD**, ticket a ticket, começando por um teste vermelho no seam principal.
- **Prior art**: ainda não há código nem testes no repositório; esta spec estabelece o padrão. O primeiro ticket deve deixar pronto o esqueleto do projeto Django, o executor de testes e um exemplo de teste de caso de uso para os demais seguirem.

## Out of Scope

- Consultar o Pedido de outro Gestor (pedidos públicos entre Gestores); o modelo não deve impedir isso depois.
- Frete compartilhado e avisos entre Gestores.
- Geração de Pedido no formato de cada Fornecedor (ADR-0004).
- Importação do histórico antigo de pedidos desde 2001 e reimportação de planilhas de Pedido editadas no Excel; o formato fixo da exportação permite um leitor futuro.
- Sugestão automática de vínculo entre Ofertas por descrição ou foto (ADR-0003).
- Distinção entre Produto idêntico e semelhante.
- Impostos (IPI, ICMS, DIFAL) e frete no Preço unitário (ADR-0005).
- Teto de compra por Produto, categoria ou Loja.
- Dados de venda; o sistema só conhece Pedidos de compra.
- ~~Ligar fotos vindas de um arquivo separado só de fotos às Ofertas~~ (passou a fazer parte do MVP pelo ADR-0010).
- Ligar foto à Oferta por semelhança aproximada de descrição ou de imagem; e lembrar, para os próximos Catálogos, uma ligação de foto feita à mão.
- Saber que um item saiu de linha: um código que não está no Catálogo mais recente continua vigente pelo anterior (ADR-0009).
- Tratar um Catálogo novo como "versão" de outro, que substitui o anterior inteiro.
- Dividir o arquivo de um Representante (ou a planilha de um distribuidor com várias marcas) em Catálogos de vários Fornecedores; a marca de cada linha é parte da descrição.
- Data do Catálogo futura (preços que só valem a partir de um dia).
- Restringir quais Gestores podem alterar dados do grupo (Perfil, vínculos, Conteúdo, Teto).
- Autocadastro de usuários e recuperação de senha por e-mail.

## Further Notes

- **Categoria** aparece no briefing ("volume de pedidos por loja e por categoria"), mas não existe no `GLOSSARY.md` nem em nenhum ADR. Por isso os painéis do MVP agrupam por Fornecedor e por período, não por categoria. Se a gestora precisar desse corte, o termo deve ser definido antes com `/domain-modeling`: é atributo do Produto, do Fornecedor ou do Catálogo?
- A escolha do Claude Haiku segue o critério do ADR-0006 (menor custo com leitura de imagem) e foi confirmada pela usuária. Fica atrás de uma interface para que a troca de provedor não afete o resto do sistema.
- O registro de que catálogos de layout livre são enviados a um serviço externo, autorizado pela gestora, está no ADR-0006. A chave de API não entra no repositório.
- Os limites de "preço muito fora do padrão do próprio Catálogo" e a regra de "descrição cita peças" são heurísticas; o ticket correspondente deve fixá-las com exemplos fictícios e mantê-las simples de explicar.
- **Mudança de requisito de 2026-11-05** (ADR-0009, ADR-0010, ADR-0011): data do Catálogo informada, vigência pelo Catálogo mais recente, Catálogo sem preço completado por planilhas de preços, foto em todos os caminhos. A numeração das histórias foi mantida; as novas vão de 101 a 118. O caso real que motivou o código opcional e as várias planilhas é um distribuidor com um PDF de 48 páginas só com fotos e descrições, sem código, e duas planilhas em formatos diferentes (principal e promoção). Ler esse PDF pela LLM, pedindo também a área de cada foto, entra na medição de tempo e custo por página.
- Próximos passos do processo: `/c4-from-spec` (Contexto e Container) e depois `/to-tickets` em fatias verticais.
