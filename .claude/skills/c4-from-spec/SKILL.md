---
name: c4-from-spec
description: Gera os diagramas C4 de Contexto (nível 1) e Container (nível 2), em Mermaid, a partir da especificação, do glossário e dos ADRs, ANTES de existir código. Use depois do /to-spec e antes do /to-tickets.
disable-model-invocation: true
argument-hint: "[caminho do spec, opcional]"
allowed-tools: Read Glob Grep Write Edit
---

# C4 a partir da especificação

Você vai desenhar a arquitetura **planejada** do sistema, nos níveis 1 (Contexto) e 2 (Container) do Modelo C4. Ainda não existe código: tudo deve vir dos documentos do projeto. Os níveis 3 (Componentes) e 4 (Código) ficam para o fim do projeto e **não** fazem parte desta skill.

## Material disponível

Glossário do domínio:
!`cat GLOSSARY.md 2>/dev/null || echo "(GLOSSARY.md ainda não existe)"`

ADRs existentes:
!`ls docs/adr 2>/dev/null || echo "(nenhum ADR ainda)"`

Arquivos de spec e tickets em .scratch/:
!`find .scratch -name "*.md" 2>/dev/null | head -40 || true`

Spec indicado pela usuária (pode estar vazio): $ARGUMENTS

## Processo

1. **Leia as fontes, nesta ordem:** o spec (o caminho em `$ARGUMENTS` ou, se estiver vazio, o spec mais recente em `.scratch/`); todos os ADRs em `docs/adr/`; e `docs/BRIEFING.md`, só para ver os requisitos da disciplina e o que está fora do MVP. Se não houver spec, **pare** e peça para rodar `/to-spec` primeiro.

2. **Monte o inventário antes de desenhar.** Mostre à usuária uma tabela com cada elemento: tipo (Pessoa, Sistema, Sistema externo, Container, Banco de dados), nome, responsabilidade e **origem**. A origem é a história de usuário, o ADR ou a seção do spec que justifica o elemento. Marque como **inferido** tudo que não estiver escrito em algum documento.

3. **Pergunte só o que bloqueia** (no máximo 5 perguntas, uma por vez). Por exemplo: uma tecnologia que nenhum ADR definiu, ou um sistema externo que não está claro. Não invente uma tecnologia para preencher lacuna: use "a decidir" e sugira registrar um ADR.

4. **Escreva os diagramas** em `docs/architecture/`:
   - `c4-1-contexto.md`
   - `c4-2-container.md`

   Use a sintaxe do `reference.md` (ao lado deste arquivo; leia antes de escrever). Cada arquivo tem: o diagrama em Mermaid, uma tabela de elementos (nome, responsabilidade, origem), uma lista **Suposições e pontos inferidos** e uma lista **Perguntas em aberto**.

5. **Confira a checklist** abaixo e corrija o que falhar antes de dar por concluído.

6. **Resuma em até 6 linhas:** os elementos criados, as suposições, as perguntas em aberto e se algum ADR novo deveria ser escrito.

## Regras

- **Vocabulário:** use os termos do `GLOSSARY.md` exatamente como estão escritos lá (nomes de pessoas, sistemas e responsabilidades). Se precisar de um termo novo, avise; não crie sinônimos.
- **Contexto (nível 1):** só o sistema como uma caixa, as pessoas e os sistemas externos. Nada de tecnologia, banco de dados ou módulos internos.
- **Container (nível 2):** só unidades que rodam ou guardam dados de forma independente (aplicação web, API, worker, banco, armazenamento de arquivos). Bibliotecas, classes e módulos internos **não** são containers.
- Toda relação tem um verbo no rótulo ("envia catálogo para", "lê preços de"). No nível 2, ela também tem o protocolo ou a tecnologia, quando já estiver decidido.
- Itens marcados no briefing como **fora do MVP** só entram se o spec os incluir. Se entrarem, use uma descrição que deixe claro que é uma fase futura.
- Dados reais de fornecedores ou pessoas da família nunca aparecem nos diagramas. Use papéis ("Gestora de compras", "Outro gestor do grupo").
- Escreva em português.

## Checklist

- [ ] Todo container tem pelo menos uma história de usuário ou um ADR como origem.
- [ ] Toda pessoa e todo sistema externo do nível 1 aparece também no nível 2.
- [ ] Nenhuma tecnologia foi escolhida sem um ADR ou sem estar marcada como "a decidir".
- [ ] Nenhum elemento do nível 3 (componente, classe, módulo) vazou para o nível 2.
- [ ] Os requisitos da disciplina estão visíveis: autenticação, persistência e pelo menos 3 responsabilidades distintas.
- [ ] O Mermaid usa apenas a sintaxe do `reference.md`.
