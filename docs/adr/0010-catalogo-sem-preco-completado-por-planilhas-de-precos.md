---
status: accepted
---

# Catálogo sem preço completado por planilhas de preços, numa única Revisão

Substitui, no ADR-0006, as regras "o arquivo de preços é o Catálogo", "documento sem preço continua não sendo importável" e "Catálogos com várias colunas de preço não pedem desconto". Vários Fornecedores mandam um PDF com fotos e descrições, sem preço, e os preços em uma ou mais planilhas à parte. No caso real que motivou a mudança, nenhuma das fontes tem código do Fornecedor: a gestora acha cada item no PDF pela descrição, dentro da marca indicada no canto da página. Recusar o PDF obrigava a gestora a perder as fotos. Decidimos:

1. **Arquivo do Catálogo** é o primeiro arquivo da Importação: de preferência PDF, mas Excel e imagem também são aceitos, com um aviso quando não é PDF. Ele pode trazer tudo ou só fotos e descrições.
2. Depois de lê-lo, a Importação sempre oferece **enviar planilhas de preços** ou **pular**. Pular só não é possível quando a leitura achou produtos e **nenhum** preço. Esse é o critério de "Catálogo sem preço": é decidido pelo resultado da leitura, não pelo tipo de arquivo. Um arquivo que não abre continua sendo erro, e um arquivo em que alguns produtos não têm preço continua sendo uma Revisão normal, em que a Oferta sem preço bloqueia a confirmação.
3. Pode haver **mais de uma planilha de preços**, com confirmação da gestora. Todas formam **um** Catálogo, com uma data só. Cada planilha é lida pelo leitor de tabela, com o seu mapeamento de colunas.
4. Quando há planilhas, **as planilhas criam as Ofertas** (código, descrição, preço e Caixa). O arquivo do Catálogo só dá a foto. Se ele também tiver preço e o preço for diferente do da planilha, a Oferta recebe a marca "preço diferente no Catálogo", que não bloqueia.
5. A foto se liga à Oferta **pelo código** quando ele existe nas duas fontes. Senão, pela **descrição normalizada** (sem acento, sem maiúsculas e sem espaços duplicados), dentro da marca da página quando houver, e só quando ela é **igual e única** nas duas fontes. Nunca por semelhança aproximada.
6. Item só na planilha vira Oferta sem foto. Foto sem Oferta vai para uma lista na Revisão, em que a gestora pode ligá-la à mão a uma Oferta sem foto, trocar ou tirar fotos ligadas, ou deixar sem ligar. Nada disso bloqueia a confirmação.
7. O **código** passa a ser opcional no mapeamento. Sem ele, a descrição normalizada é o código da Oferta: vigência, Conteúdo, vínculo de Produto e histórico usam essa chave. A descrição pode vir de várias colunas, juntadas em ordem (por exemplo, marca, descrição, sabor e gramatura).
8. O Perfil do Fornecedor guarda **vários mapeamentos**, cada um reconhecido pelos cabeçalhos da planilha. Na Importação vale o mapeamento cujas colunas existem todas na planilha; se nenhum servir, a gestora indica um novo, que é guardado junto dos outros.
9. O desconto das Condições do Catálogo é perguntado **sempre**, uma vez **por arquivo de onde saem as Ofertas**, e cada resposta é obrigatória (0 vale). Cada Oferta usa o desconto do seu arquivo. Quando um arquivo tem várias colunas de preço, vale a menor de cada linha, e o campo avisa que essa coluna pode já ter desconto.
10. Todos os arquivos (o arquivo do Catálogo e as planilhas) são arquivos de origem do Catálogo, guardados para sempre, cada um com o seu papel.

## Opções consideradas

- **Manter a recusa do documento sem preço (ADR-0006):** a gestora continuaria sem as fotos dos Fornecedores que mandam fotos e preços separados, que são justamente os catálogos maiores.
- **O PDF cria as Ofertas e a planilha só dá o preço:** a Caixa e o código estão na planilha ou em lugar nenhum.
- **Ligar foto por semelhança de descrição:** liga mais fotos, mas uma foto errada numa Oferta é pior que nenhuma, porque a gestora compra pelo que vê.
- **Exigir código, ou usar o número da linha como código:** o primeiro deixa de fora o caso real; o segundo muda a cada versão da planilha e quebra todos os vínculos sem aviso.
- **Um mapeamento por Fornecedor:** o caso real já tem dois formatos de planilha do mesmo Fornecedor, e a gestora remapearia a cada Importação.
- **Um desconto por Catálogo, e nenhum quando há várias colunas de preço:** não resolve um Catálogo com uma planilha de promoção (preço já final) e uma principal (com desconto negociado).

## Consequências

- Sem código, uma mudança mínima na descrição feita pelo Fornecedor faz o item virar outro: o Conteúdo, o Produto e o histórico não passam para a versão nova. Na exportação do Pedido, a coluna de código sai vazia e a descrição identifica o item.
- Dividir o arquivo de um Representante em Catálogos de vários Fornecedores continua fora do escopo. Uma marca listada numa planilha (como a coluna de fornecedor de um distribuidor) é parte da descrição, não um Fornecedor.
- Com o desconto sempre perguntado, a gestora pode aplicá-lo duas vezes num Catálogo com várias colunas de preço. O aviso no campo é a única proteção.
- A ligação manual de uma foto vale só para aquela Revisão; não é lembrada nos próximos Catálogos.
