# 08 — Marcas de conferência e contagem de preços na Revisão

Status: resolved
Type: task
Blocked by: 06, 07
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › marcas de conferência; Further Notes › heurísticas)
ADRs: ADR-0006 (marcas e contagem), ADR-0005 (Conteúdo padrão 1)
User stories: 30 (fora do padrão), 32, 33, 43

## O que entrega

A Revisão aponta o que a gestora deve olhar com atenção: preço muito fora do padrão do próprio Catálogo, Unidade de venda ambígua e descrição que cita peças. Ela também mostra quantos preços havia no arquivo e quantas Ofertas foram extraídas.

O spec delega a este ticket a definição das heurísticas, com exemplos fictícios e de forma fácil de explicar. As regras abaixo são a proposta e podem ser ajustadas antes da sessão de TDD.

## Critérios de aceite

- **Preço fora do padrão** (30): quando o Catálogo tem pelo menos 5 Ofertas com preço, fica marcada a Oferta cujo preço impresso é mais de 10 vezes a mediana dos preços do Catálogo, ou menos de 1/10 dela. Ofertas sem preço não entram na mediana. (Fator ajustado na calibração; ver abaixo.)
  - Exemplo: preços 9, 10, 10, 11, 12 e 150 → só a de 150 é marcada.
  - Com só 3 Ofertas com preço, nada é marcado como fora do padrão.
- **Unidade de venda ambígua** (32): fica marcada a Oferta cuja descrição tem, como palavra inteira, KIT, CJ, CONJUNTO, SET ou PAR, ignorando maiúsculas e acentos. (JOGO saiu e CJ entrou na calibração; ver abaixo.)
- **Sugestão de Conteúdo** (43): quando a descrição cita uma quantidade de peças ("C/3", "COM 3 PEÇAS", "3 PÇS", "3 PCS", "3 UNID"), a Revisão sugere Conteúdo 3. A sugestão só aparece se o Conteúdo ainda for 1 e não houver decisão guardada para esse Fornecedor + código. Aceitar a sugestão é definir o Conteúdo (ticket 07). O sistema nunca muda o Conteúdo sozinho (42).
- **Manter 1** (decisão da usuária): ao lado de "Aceitar", a sugestão tem "Manter 1", que guarda no histórico do Conteúdo daquele Fornecedor + código uma decisão explícita de manter 1, com Gestor e data. Com essa decisão guardada, a sugestão não reaparece nos próximos Catálogos. É a exceção à regra do ticket 07 de que nada é registrado quando o valor não muda.
- **Contagem** (33): no caminho de grade de cartões, a Revisão mostra "Preços no arquivo: N · Ofertas extraídas: M", contando as ocorrências de preço no texto do PDF. Quando M < N, a diferença fica destacada.
- As marcas são recalculadas depois de cada correção: corrigir o preço tira a marca de "fora do padrão".
- As marcas de fora do padrão, ambígua e sugestão de Conteúdo **não** impedem a confirmação. A Oferta sem preço continua impedindo (ticket 06).

## Erros (mensagens em português)

- Confirmar com uma Oferta marcada como fora do padrão: a confirmação passa.
- Confirmar com uma Oferta sem preço continua recusado → `Informe um preço maior que zero antes de confirmar. Ofertas sem preço: 1003.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com descrições e preços inventados escolhidos para cada regra: um preço fora do padrão, uma descrição com "KIT", uma com "C/3", um Catálogo com só 3 preços e um PDF com um preço que o leitor não transforma em Oferta (para M < N).
- Nenhum fake da LLM.

## Fora deste ticket

- Contagem nos caminhos de tabela (21) e LLM (25).

## Calibração com os Catálogos reais (2026-11-05)

Medida localmente com `ferramentas/conferir_catalogos_reais.py` nos 8 PDFs reais do Layout A (1.931 Ofertas). Só números; nenhum dado real.

| Regra | Proposta original | Regra final |
|---|---|---|
| Fora do padrão | 5× / 1/5: 139 (7,2%); passou de 10% em 3 Catálogos (15,7%, 16,7%, 15,0%) | **10× / 1/10: 48 (2,5%)**; maior Catálogo marcado: 9,3% (o de 20 Ofertas fica com 3 = 15%) |
| Ambígua | KIT, JOGO, CONJUNTO, SET, PAR: 118 (6,1%); um Catálogo com 27,1% (JOGO: 29) | **KIT, CJ, CONJUNTO, SET, PAR: 93 (4,8%)**; maior Catálogo de tamanho real: 9,6% |
| Sugestão de Conteúdo | 248 (12,8%): "N PÇS/PCS" 226, "C/N" 17, "COM N PEÇAS" 5, "N UNID" 0 | **Mantida** (decisão da usuária), com "Manter 1" para não repetir |
| Preços no arquivo × Ofertas | 1.931 × 1.931 nos 8 arquivos | **Preço mascarado ("R$***,**") conta como preço no arquivo** (1 no real), porque vira Oferta sem preço |

- **Por que 10×:** os Catálogos reais têm faixas largas de verdade (num deles, o maior preço é 80× a mediana); o erro de leitura típico, vírgula deslocada, é ×10 ou ×100. Alternativas medidas: 8× = 65; 15× = 33; 20× = 24.
- **Por que sem JOGO:** no real, 30 das 32 ocorrências não citam peças e nenhuma é "JOGO DE": é brinquedo, não conjunto. **CJ** (conjunto) aparece 7 vezes, todas com número de peças.
- **Sugestão:** ajustes medidos não ficaram abaixo de 10% sem tirar "N PÇS" (2 a 12: 11,5%; sem KIT/JOGO: 10,0%; os dois: 9,1%, com um Catálogo a 15,4%; sem "N PÇS": 1,1%). Tirar KIT contradiria o exemplo do kit de tesouras vendidas avulsas.
- **"C/N" no Layout A:** quantidade de itens que vêm na Unidade de venda ("com N <itens>", em geral no fim da descrição), nunca igual à Caixa (0 de 17). "C/" seguido de letra (266 vezes) não é quantidade e não conta.

## Comments

**2026-11-05 — implementado por TDD** (commits `ab83846` a `ca03ccc`; antes, `99438e6` Caixa "³", `ee99b47` script de conferência, `1baaa9d` calibração)

- **Regras** (`importacao/marcas.py`, derivadas, sem coluna): `mediana_dos_precos` (sem preço e zero não entram; menos de 5 preços = sem padrão), `fora_do_padrao` (10×, 1/10), `unidade_ambigua` (KIT, CJ, CONJUNTO, SET, PAR), `pecas_citadas` (C/N, COM N PEÇAS, N PÇS/PCS, N UNID; quantidade > 1).
- **Na Oferta proposta:** `marcas` ("sem preço", "preço zero", "fora do padrão", "unidade ambígua"), recalculadas a cada leitura; `sugestao_de_conteudo` só com Conteúdo 1, sem decisão guardada e sem "Manter 1".
- **Aceitar** (`aceitar_sugestao_de_conteudo`): define o Conteúdo na Revisão pelo Corrigir do ticket 07; guardado ao confirmar. Repetir não desfaz.
- **Manter 1** (`manter_conteudo_1`; decisão da usuária): campo `decidiu_manter_conteudo_1` na Oferta proposta; ao confirmar, grava 1 → 1 no histórico (`guardar_conteudo(..., decisao_explicita=True)`). Como o Aceitar, fica na Revisão até a confirmação; abandonar descarta (decisão da usuária).
- **Contagem:** a Extração devolve `Extracao(ofertas, precos_no_arquivo)` (`extrair_catalogo`); a Revisão guarda `precos_no_arquivo` e `ofertas_extraidas` na Importação (o arquivo não é relido a cada tela) e expõe `ofertas_que_faltam`.
- **Confirmação:** fora do padrão, ambígua e sugestão não bloqueiam; sem preço continua bloqueando.
- **Telas:** "unidade ambígua" na célula da descrição, marcas de preço na do preço, linha em alerta; "Sugestão: Conteúdo N" com "Aceitar" e "Manter 1" (botões secundários pequenos) na célula do Conteúdo; contagem no topo, em alerta com "Falta(m) N Oferta(s): confira o arquivo." quando M < N.
- **Conferência no fim:** o script, agora usando as regras da aplicação, lê os mesmos números de antes (8 PDFs, 1.931 Ofertas, 1 sem preço, 2 sem Caixa) e reproduz a calibração final.
