# 14 — Foto da Oferta lida da grade de cartões

Status: ready-for-agent
Type: task
Blocked by: 11, 13, 31
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Foto; Modelo de dados › Oferta: foto opcional, Foto)
ADRs: ADR-0011 (foto em todos os caminhos, guardada como arquivo; aqui, o caminho da grade). Substitui, neste ticket, a regra do ADR-0006 de que só o arquivo de preços dá foto.
User stories: 57 (foto), 65 (foto), 116 (grade de cartões), 118
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

Quando o cartão do Catálogo tem foto, ela aparece na Revisão, na busca e na comparação do Produto, para a gestora reconhecer o produto sem abrir o arquivo. As fotos ficam como arquivos, reduzidas e sem duplicar. Uma Oferta sem foto mostra a foto mais recente do mesmo item, vinda de um Catálogo anterior.

## Critérios de aceite

Captura e guarda

- Um cartão do Layout A com imagem gera uma Oferta proposta com foto, visível na Revisão (116).
- A foto é um arquivo em `fotos/`, na pasta de arquivos (ticket 11), nunca dentro do banco. É guardada reduzida (lado maior até 600 px, JPEG) e nomeada pela impressão digital do conteúdo; a Oferta guarda só a referência.
- A mesma imagem num Catálogo seguinte não é guardada de novo: as duas Ofertas apontam para o mesmo arquivo.
- Ao confirmar, a foto fica guardada para sempre e aparece nos resultados da busca (57) e na comparação do Produto (65).
- Abandonar a Revisão apaga as fotos que só ela usava; uma foto que um Catálogo confirmado também usa não é apagada.
- Um cartão sem imagem gera uma Oferta sem foto, sem erro nem marca.
- A foto não entra em nenhum cálculo nem em nenhuma comparação.
- Depois de backup e restauração (ticket 11), a foto da Oferta continua aparecendo na busca.

Foto de Catálogo anterior (118)

- Uma Oferta sem foto **mostra**, na busca e na comparação do Produto, a foto mais recente do mesmo Fornecedor + código vinda de um Catálogo anterior (o mais recente pela data do Catálogo, ticket 31), com a legenda `Foto do Catálogo de 15/10/2026`.
- Nada é copiado para a Oferta: a foto mostrada é calculada na exibição. Se o Catálogo novo trouxer foto, vale a dele.
- A Revisão mostra só o que o arquivo trouxe, sem a foto de Catálogo anterior.
- O mesmo código de outro Fornecedor nunca empresta a foto.

## Erros (mensagens em português)

- Nenhum erro novo: falta de imagem não é erro. A recusa de "PDF só com fotos" saiu deste ticket; o arquivo sem preço passa a pedir a planilha de preços (ticket 36).

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, agora com imagem opcional por cartão: uma imagem pequena gerada no próprio teste (por exemplo, um quadrado colorido), e outra maior que 600 px para conferir a redução.
- Dois Catálogos do mesmo Fornecedor com datas diferentes: o anterior com foto, o novo sem foto para o mesmo código; e um segundo Fornecedor com o mesmo código.
- Pasta de arquivos temporária e o comando de backup do ticket 11.
- Nenhum fake da LLM.

## Fora deste ticket

- Trocar ou tirar a foto na Revisão (34).
- Fotos nos caminhos de tabela (39) e LLM (25, 26).
- Ligar as fotos do arquivo do Catálogo às Ofertas da planilha de preços (38).
- Foto no Pedido (a mesma exibição, quando o ticket 16 mostrar a Oferta).
