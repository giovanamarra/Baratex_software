# 26 — Conferir as páginas lidas pela LLM ao lado da imagem

Status: ready-for-agent
Type: task
Blocked by: 25, 34
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › confirmação recusada com página não conferida; Revisão › Fotos)
ADRs: ADR-0006 (conferência ao lado da imagem é obrigatória e não pode ser pulada em lote), ADR-0011 (item 2: a foto recortada pela LLM passa pela conferência)
User stories: 28, 29, 117 (fotos recortadas pela LLM)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora confere cada página lida pela LLM com a imagem original ao lado, inclusive as fotos recortadas. A confirmação só passa depois que todas as páginas foram conferidas, para um preço errado mas plausível, ou a foto do item vizinho, não passar despercebido.

## Critérios de aceite

- A Revisão lista as páginas lidas pela LLM. Cada uma traz a imagem da página e as Ofertas que vieram dela (28).
- Marcar página como conferida (Gestor, Revisão, página) marca uma página por vez. Não existe caso de uso nem botão para conferir todas de uma vez (29).
- A confirmação é recusada enquanto houver página lida pela LLM sem conferência.
- Preço errado plausível: o fake devolve 12,90 para uma Oferta que no Catálogo fictício custa 21,90. A Oferta aparece com 12,90 e sem marca automática. A gestora corrige para 21,90 e marca a página, e só então a confirmação passa.
- Ofertas adicionadas à mão, ou de outros caminhos, não exigem conferência de página.
- **Fotos recortadas** (117): na conferência, cada Oferta da página aparece com a foto recortada pela LLM, ao lado da imagem da página. A gestora troca ou tira a foto errada pelo caso de uso do ticket 34, sem sair da conferência.
- Foto errada: o fake devolve para a Oferta 1002 a área da foto da Oferta 1003. A gestora troca a foto, marca a página, e a confirmação passa com a foto trocada.
- Trocar ou tirar a foto não marca a página como conferida; marcar a página continua sendo um passo à parte.

## Erros (mensagens em português)

- Confirmar com páginas não conferidas → `Confira as páginas 2 e 5, lidas pela LLM, antes de confirmar.`
- Marcar uma página que não existe na Revisão → `A página 9 não existe nesta Revisão.`

## O que o teste precisa

- **Fake da LLM** com respostas fixas para um PDF fictício de 5 páginas sem texto, incluindo o preço errado plausível e a área de foto trocada entre duas Ofertas.
- Nenhum teste chama a API real.
