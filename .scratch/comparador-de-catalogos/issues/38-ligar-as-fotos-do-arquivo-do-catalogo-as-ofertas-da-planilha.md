# 38 — Ligar as fotos do arquivo do Catálogo às Ofertas da planilha

Status: ready-for-agent
Type: task
Blocked by: 34, 35, 36
Spec: [docs/spec.md](../../../docs/spec.md) (Catálogo em mais de um arquivo › De onde saem as Ofertas, Ligação da foto, Só numa fonte; Extração › marcas de conferência)
ADRs: ADR-0010 (itens 4, 5 e 6), ADR-0011
User stories: 111, 112, 113
Muda código já feito: ticket 08 (marca nova "preço diferente no Catálogo", que não bloqueia). O ticket continua resolvido.

## O que entrega

Quando há planilha de preços, as fotos do arquivo do Catálogo vão para as Ofertas certas: pelo código ou, sem código, pela descrição igual e única. As fotos que não acharam Oferta ficam numa lista, de onde a gestora pode ligá-las à mão. Nunca uma foto vai para o item errado por semelhança.

## Critérios de aceite

Ligação automática (111)

- (1) **Pelo código**, quando o arquivo do Catálogo e a planilha têm código: a foto do item 1001 do arquivo do Catálogo vai para a Oferta 1001 da planilha.
- (2) Senão, pela **descrição normalizada** (ticket 35), só quando ela é **igual e única** nas duas fontes.
  - `Balde Azul 10L` uma vez em cada fonte → liga.
  - `Balde Azul 10L` duas vezes no arquivo do Catálogo, ou duas vezes na planilha → não liga nenhuma das duas.
  - `Balde Azul 10L` contra `Balde Azul 10 L` → não liga.
- (3) Nunca por semelhança aproximada.
- A Revisão mostra o resumo `Fotos ligadas: 46 de 77 Ofertas.`

Só numa fonte (113)

- Oferta da planilha sem foto ligada → Oferta normal sem foto, sem marca.
- Foto do arquivo do Catálogo sem Oferta → seção `Fotos do catálogo sem preço na planilha (N)`, com a foto e a descrição lida.
- Dessa seção, a gestora liga uma foto a uma Oferta **sem foto**. As fotos ligadas podem ser trocadas ou tiradas como no ticket 34.
- Fotos não ligadas são descartadas ao confirmar (as que só a Revisão usava; regra de abandono do ticket 34).
- A ligação manual vale só para esta Revisão; não é lembrada nos próximos Catálogos.
- Nada disso bloqueia a confirmação.

Preço diferente no Catálogo (112)

- Quando a Oferta ligada também tem preço no arquivo do Catálogo e ele é diferente do preço impresso da planilha, a Oferta recebe a marca `preço diferente no Catálogo: R$ X,XX` (o preço do arquivo do Catálogo). Vale o preço da planilha. A marca não bloqueia.
- Preços iguais, ou arquivo do Catálogo sem preço, não dão marca.

## Erros (mensagens em português)

Texto proposto (o spec não escreve):

- Ligar uma foto a uma Oferta que já tem foto → `Esta Oferta já tem foto. Tire a foto atual antes de ligar outra.`

## O que o teste precisa

- O arquivo do Catálogo fictício do Layout A com imagem por cartão (ticket 14), com e sem preço; planilhas fictícias em Excel com e sem coluna de código; descrições repetidas numa das fontes; uma descrição que difere só por um espaço.
- Nenhum fake da LLM.

## Fora deste ticket

- Ligação "dentro da marca da página", que só existe quando a LLM devolve a marca (25).
- Ligar por semelhança de descrição ou de imagem; lembrar ligações manuais (Out of Scope).
