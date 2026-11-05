# 36 — Completar o Catálogo com uma planilha de preços

Status: ready-for-agent
Type: task
Blocked by: 21, 31
Spec: [docs/spec.md](../../../docs/spec.md) (Catálogo em mais de um arquivo › Fluxo, Planilha de preços, De onde saem as Ofertas; Extração › Catálogo sem preço; Modelo de dados › Catálogo: arquivos de origem)
ADRs: ADR-0010 (itens 1, 2, 4 sem fotos e 10)
User stories: 14 (aviso quando não é PDF), 21, 109, 115
Muda código já feito: tickets 03 (a recusa de "documento sem preço" vira o pedido de planilha; aviso quando não é PDF) e 08 (a contagem vem da planilha). Esses tickets continuam resolvidos.

## O que entrega

Depois de enviar o arquivo do Catálogo, a gestora sempre pode enviar uma planilha de preços ou pular. Quando o arquivo tem produtos mas nenhum preço, a planilha é exigida. As Ofertas saem da planilha, e os dois arquivos ficam guardados no Catálogo, cada um com o seu papel.

## Critérios de aceite

Envio do arquivo do Catálogo (14)

- Um arquivo do Catálogo que não é PDF (Excel ou imagem) mostra o aviso abaixo, com "Prosseguir" e "Trocar arquivo". Prosseguir segue a Importação normalmente; um PDF não tem aviso.

Enviar planilha ou pular (109, 21)

- Depois de ler o arquivo do Catálogo, a Importação pergunta `Tem uma planilha de preços para completar este Catálogo?`, com [Enviar planilha] e [Pular].
- Pular segue como hoje: as Ofertas saem do arquivo do Catálogo.
- **Catálogo sem preço**: a leitura achou produtos (código ou descrição) e **nenhum** preço. Aí não há "Pular": a Importação exige a planilha, com a mensagem abaixo. Nenhum Catálogo sem preço é criado.
- Alguns produtos sem preço não é Catálogo sem preço: é Revisão normal, com a Oferta sem preço bloqueando (ticket 06), como o `R$***,**` do Layout A.
- Arquivo que não abre e leitura sem nenhum produto continuam sendo os erros de Importação de hoje.
- A pergunta é decidida pelo resultado da leitura, não pelo tipo de arquivo.

Com a planilha

- A planilha de preços é lida pelo leitor de tabela, com o mapeamento do Perfil do Fornecedor ou um novo indicado pela gestora (ticket 21). Neste ticket ela é .xlsx; o PDF em tabela passa a valer como planilha de preços no ticket 23.
- **As Ofertas saem só da planilha** (código, descrição, preço, Caixa), com o caminho "tabela". O arquivo do Catálogo não cria Ofertas; as fotos dele são ligadas no ticket 38.
- A contagem "Preços no arquivo" é a da planilha.
- O desconto das Condições do Catálogo é o da planilha (um só, como hoje; vários no ticket 37), obrigatório.
- A data do Catálogo é uma só para o Catálogo (ticket 31).

Arquivos de origem (115)

- O Catálogo guarda o arquivo do Catálogo e a planilha de preços, cada um com o seu papel ("arquivo do Catálogo", "planilha de preços"), para sempre.
- A página do Catálogo lista os arquivos de origem com o papel e o nome original, e abre cada um.
- Abandonar a Revisão apaga os dois arquivos.
- Os Catálogos que já existem ficam com o seu arquivo no papel "arquivo do Catálogo".

## Erros (mensagens em português)

- Arquivo do Catálogo que não é PDF (aviso, não erro) → `O arquivo enviado não é um PDF. O Catálogo costuma vir em PDF, com as fotos; a planilha de preços, quando houver, é pedida depois. Deseja prosseguir com este arquivo?`
- Catálogo sem preço → `Este arquivo não tem preços. Envie a planilha de preços para continuar.` (substitui `Este documento não tem preços, então não é um Catálogo...` dos tickets 03 e 21)
- Texto proposto (o spec não escreve):
  - Planilha que não é .xlsx (nem PDF em tabela, depois do ticket 23) → `A planilha de preços precisa ser um arquivo .xlsx ou um PDF em tabela.`
  - Planilha sem nenhum preço numérico → `Esta planilha não tem preços. Confira se enviou a planilha de preços certa.`
- `.xls` antigo como planilha → a mesma mensagem do ticket 21.

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A com cartões sem preço (produtos sem nenhum preço) e com preço; o Catálogo fictício em tabela Excel do ticket 21 como planilha de preços.
- Um Excel e uma imagem como arquivo do Catálogo, para o aviso.
- Nenhum fake da LLM.

## Fora deste ticket

- Mais de uma planilha e desconto por arquivo (37).
- Ligar as fotos do arquivo do Catálogo às Ofertas da planilha e a marca "preço diferente no Catálogo" (38).
- Catálogo sem preço lido pela LLM (25).
- Dividir o arquivo de um Representante em vários Fornecedores (Out of Scope).
