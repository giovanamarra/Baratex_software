# Briefing do projeto: Comparador de Catálogos de Fornecedores

> Documento de entrada para o agente. **Não é a especificação.** É o material bruto que a skill `/grill-with-docs` deve interrogar e transformar em `GLOSSARY.md`, ADRs e, depois, no spec (`/to-spec`).
> Tudo aqui pode ser questionado. Onde está escrito "hipótese", ainda não foi confirmado.

---

## 1. Contexto

- **Usuária principal (MVP):** minha mãe, gestora de compras de uma rede de lojas do mesmo grupo familiar. Ela gerencia **3 lojas** (ex.: uma em BH e lojas em Betim).
- **Outros gestores do grupo:** sócios que também fazem pedidos aos mesmos fornecedores. Hoje trocam planilhas e mensagens entre si.
- **Projeto acadêmico:** disciplina *Métodos e Aplicações de IA* (Eng. de Computação). O processo de desenvolvimento com skills é avaliado tanto quanto o software.

## 2. A dor central

1. Cada fornecedor manda o catálogo em um formato diferente (hipótese: PDF, planilha Excel, imagens/fotos). E cada fornecedor também pede o pedido em uma planilha diferente.
2. Para cada produto, ela tem um **preço máximo de compra** que ainda dá lucro.
3. Para decidir, ela abre vários catálogos, procura o produto que gostou e faz contas à mão. Exemplo: "kit com 3 tesouras por R$ 9,00" = R$ 3,00 por tesoura. Aí compara se vale mais o kit ou a tesoura avulsa, do mesmo fornecedor ou de outro.
4. Ela tem **histórico de pedidos desde 2001**, mas não consegue usá-lo para ver evolução de preço ou o melhor fornecedor.
5. Ela "sabe na prática" que algumas lojas vendem mais de certas categorias (ex.: BH pede 2 ou 3 caixas de acessórios quando Betim pede 1) e que há épocas do ano que vendem mais. Mas isso não está registrado em lugar nenhum.

## 3. Regras de negócio já conhecidas (a refinar)

- **Preço unitário:** preço do item ÷ quantidade por embalagem/kit. Toda comparação deve ser feita no preço unitário.
- **Teto de compra:** cada produto tem um preço máximo aceitável. Ofertas acima do teto devem ficar destacadas.
- **Kit × avulso:** o sistema deve mostrar qual opção sai mais barata por unidade, entre fornecedores e dentro do mesmo fornecedor.
- **Produto igual × semelhante:** o mesmo produto aparece com códigos e descrições diferentes em cada fornecedor. É preciso um jeito de dizer que "esta oferta é o mesmo produto que aquela".
- **Histórico de preço:** cada catálogo importado é uma "foto" do preço naquela data. Não sobrescrever: guardar a série histórica.

## 4. Escopo do MVP (entrega da disciplina)

1. **Login e perfis:** um usuário pode ter várias lojas associadas.
2. **Importação de catálogo:** upload do arquivo do fornecedor → extração para uma tabela padrão (código, descrição, preço, quantidade por embalagem, preço unitário, imagem quando houver) → **tela de revisão** onde a usuária confirma ou corrige o mapeamento antes de salvar.
3. **Catálogo consolidado:** busca de produtos, comparação entre fornecedores pelo preço unitário e alerta de teto de compra.
4. **Histórico:** registro dos catálogos e pedidos com data. Importação de histórico antigo (formato a definir).
5. **Dashboards por loja:** evolução de preço por produto e fornecedor, comparação entre fornecedores e volume de pedidos por loja e por categoria.

## 5. Fora do MVP (fases futuras, mas a modelagem não deve impedir)

- **Pedidos públicos entre gestores:** um gestor consulta o pedido de outro (ex.: "o pedido de nacionais"), sem precisar pedir por mensagem.
- **Frete compartilhado:** ao concluir um pedido, informar o espaço que sobra no caminhão. O sistema avisa os outros gestores por e-mail ou no painel, só para eles combinarem entre si. A negociação continua fora do sistema.
- **Geração do pedido no formato de cada fornecedor.**
- **Expansão:** validar com minha mãe, ajustar e depois apresentar aos outros sócios do grupo.

## 6. Dúvidas em aberto (o grilling deve começar por aqui)

1. Quais formatos de catálogo existem de verdade? Em que proporção? Algum vem só como foto ou PDF escaneado?
2. Como a extração vai funcionar: parser por fornecedor, extração com LLM, ou os dois com revisão humana? O que acontece quando a extração erra?
3. Como definir que dois produtos de fornecedores diferentes são "o mesmo"? Vínculo manual, sugestão automática ou um código interno da loja?
4. O que é "semelhante" e quanto disso cabe no MVP?
5. O teto de compra é por produto, por categoria ou por loja? Quem define e onde ele está hoje?
6. Em que formato está o histórico desde 2001: planilhas, papel ou sistema antigo? Vale importar tudo ou só os últimos anos?
7. "Qual loja vende mais" vem de quê? Temos dados de **venda** ou só de **pedidos de compra**? Pedido de compra não é venda: o sistema não deve chamar uma coisa pela outra.
8. Pedido e catálogo são conceitos diferentes? Qual é o ciclo de vida de um pedido (rascunho, enviado, concluído)?
9. Imagem do produto: é obrigatória? E se o catálogo não tiver imagem?

## 7. Requisitos da disciplina (não negociáveis)

- No mínimo 3 módulos com responsabilidades distintas.
- Persistência em banco de dados.
- Regras de negócio não triviais, com tratamento de erros.
- Interface utilizável (web).
- Autenticação e autorização (um gestor não edita as lojas de outro).
- Testes automatizados das regras de negócio e dos fluxos principais (TDD).
- **Modelo C4:** Contexto e Container **antes do código**; Componentes e Código no final.
- Documentação suficiente para outra pessoa rodar e entender o sistema.
- Evidências do processo: decisões registradas em ADRs, prints das skills e mudanças de rota.

## 8. Preferências técnicas (a decidir no grilling, com ADR)

- Meu stack: Python, SQL, HTML/CSS. Também conheço Java, C e Power BI.
- Preferência por Python no backend e banco relacional (SQLite no desenvolvimento, PostgreSQL se precisar).
- Prefiro poucas peças e soluções simples a uma arquitetura sofisticada. Preciso conseguir explicar cada decisão.
- Dados reais de fornecedores e da família **não vão para o repositório**. Usar dados fictícios ou anonimizados nos testes e na demo.

## 9. Processo com skills

1. `/setup-matt-pocock-skills`: tickets como markdown local, `GLOSSARY.md` e `docs/adr/` na raiz.
2. `/grill-with-docs`: interrogatório do domínio, gerando glossário e ADRs.
3. `/to-spec`: spec do MVP.
4. `/c4-from-spec` (skill própria): diagramas C4 de Contexto e Container.
5. `/to-tickets`: fatias verticais (tracer bullets).
6. `/tdd`: implementação ticket a ticket, **uma sessão nova por ticket** (para evitar context rot).
7. `c4-codebase-architecture` (skill do lmammino): diagramas C4 de Componentes no final.