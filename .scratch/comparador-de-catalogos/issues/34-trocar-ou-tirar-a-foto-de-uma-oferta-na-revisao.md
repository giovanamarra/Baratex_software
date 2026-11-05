# 34 — Trocar ou tirar a foto de uma Oferta na Revisão

Status: ready-for-agent
Type: task
Blocked by: 14
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › Fotos; Modelo de dados › Foto)
ADRs: ADR-0011 (itens 2 e 3)
User stories: 34 (foto), 117 (trocar ou tirar)
Muda código já feito: ticket 06 (a correção da Oferta proposta passa a incluir a foto). O ticket continua resolvido.

## O que entrega

Quando a foto que veio do arquivo está errada, ou falta, a gestora troca por outra imagem ou tira a foto, antes de confirmar. Uma foto errada não entra na base.

## Critérios de aceite

- Trocar a foto de uma Oferta proposta (Gestor, Revisão, Oferta, imagem JPG ou PNG) faz a Revisão mostrar a foto nova. A imagem é guardada como as do ticket 14: reduzida (lado maior até 600 px, JPEG) e nomeada pela impressão digital do conteúdo.
- Pôr foto numa Oferta sem foto funciona do mesmo jeito.
- Tirar a foto deixa a Oferta proposta sem foto, sem marca.
- As mudanças só chegam ao Catálogo com a confirmação. Depois de confirmar, a busca e a comparação mostram a foto escolhida.
- Abandonar a Revisão apaga as fotos que só ela usava. Uma foto que também é usada por um Catálogo confirmado (mesma impressão digital) **não** é apagada.
- A Revisão mostra só o que o arquivo trouxe e o que a gestora trocou: a foto de Catálogo anterior (ticket 14) não aparece na Revisão.
- As recusas de Revisão de outro Gestor ou já confirmada valem também aqui.

## Erros (mensagens em português)

Texto proposto (o spec não escreve):

- Arquivo que não é imagem JPG ou PNG, ou que não abre → `Envie a foto em JPG ou PNG.`
- Tirar a foto de uma Oferta sem foto → `Esta Oferta não tem foto.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A com imagem opcional por cartão (ticket 14); uma imagem PNG pequena gerada no teste, maior que 600 px, para conferir a redução; bytes inválidos.
- Um Catálogo confirmado que já usa a mesma imagem, para o teste do abandono.
- Nenhum fake da LLM.

## Fora deste ticket

- Ligar à mão as fotos do arquivo do Catálogo que não acharam Oferta (38).
- Conferir as fotos recortadas pela LLM junto com as páginas (26).
