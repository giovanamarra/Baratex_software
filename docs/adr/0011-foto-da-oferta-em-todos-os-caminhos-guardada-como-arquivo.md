---
status: accepted
---

# Foto da Oferta capturada em todos os caminhos e guardada como arquivo

Até aqui, só a grade de cartões capturava foto. A gestora pediu que todo Catálogo que traz foto tenha a foto importada junto com código, descrição, preço e Caixa, porque é pela foto que ela reconhece o produto. Decidimos:

1. A foto é capturada sempre que o **arquivo do Catálogo** traz uma imagem ligada ao item: a imagem do cartão (grade), a imagem ancorada na linha (Excel), a imagem na faixa da linha (PDF em tabela) e a **área da foto devolvida pela LLM**, recortada da imagem da página. Item sem imagem vira Oferta sem foto, sem marca e sem erro. Uma planilha sem imagens não dá foto.
2. A foto recortada pela LLM passa pela conferência obrigatória das páginas lidas pela LLM. Em qualquer caminho, a gestora pode trocar ou tirar a foto na Revisão.
3. As fotos são **arquivos** na pasta de arquivos (`fotos/`), nunca dentro do banco. São guardadas reduzidas (lado maior até 600 px, JPEG) e nomeadas pela impressão digital do conteúdo, para que a mesma foto em Catálogos seguintes não seja guardada de novo. São guardadas para sempre, exceto as de uma Revisão abandonada.
4. Uma Oferta sem foto **mostra**, na busca, na comparação do Produto e no Pedido, a foto mais recente do mesmo Fornecedor + código vinda de um Catálogo anterior, com a legenda do Catálogo de origem. Nada é copiado para a Oferta, e a Revisão mostra só o que o arquivo trouxe.
5. A foto não entra em nenhum cálculo nem em nenhuma comparação.

## Opções consideradas

- **Imagem dentro do banco:** um único arquivo para copiar, mas o SQLite fica pesado e cada backup fica lento.
- **Guardar a imagem do tamanho original:** o original já fica inteiro no arquivo do Catálogo, guardado para sempre.
- **Não reaproveitar foto de Catálogo anterior:** os Fornecedores que mandam o PDF com fotos só de vez em quando teriam o mesmo item com foto num mês e sem foto no outro.

## Consequências

- O backup (que já copia a pasta de arquivos) cresce com as fotos; o primeiro Catálogo grande de um Fornecedor ocupa dezenas de MB, e os seguintes quase nada.
- Pedir a área da foto à LLM aumenta a resposta por página. O custo entra na medição de tempo e custo por página da LLM.
- A foto antiga mostrada numa Oferta sem foto pode não corresponder à embalagem atual. A legenda com a data deixa isso claro.
