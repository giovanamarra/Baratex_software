# Comparador de Catálogos de Fornecedores

Linguagem do domínio de compras de um grupo familiar de lojas, que recebe catálogos de vários fornecedores e precisa compará-los para decidir o que comprar.

## Language

### Catálogos

**Fornecedor**:
Empresa que vende produtos ao grupo. Um Fornecedor pode enviar vários Catálogos e vender várias marcas; o nome de um arquivo ou de uma marca não identifica o Fornecedor.
_Avoid_: Marca, arquivo

**Catálogo**:
Conjunto de preços enviado por um Fornecedor, datado pelo dia da sua Importação, em PDF, planilha ou imagem. Se fotos e preços chegam em arquivos separados, o Catálogo é o arquivo de preços. Um documento sem preços não é um Catálogo.
_Avoid_: Tabela, lista de preços, arquivo

**Oferta**:
Um item de um Catálogo: algo que o Fornecedor propõe vender, com o preço daquele Catálogo.
_Avoid_: Linha, item do catálogo

**Oferta vigente**:
A Oferta do Catálogo mais recente de um Fornecedor para um mesmo código; com dois Catálogos do mesmo dia, a de menor preço. É a que entra na comparação; as anteriores formam o histórico de preço.
_Avoid_: Oferta atual, preço atual

**Produto**:
Grupo de Ofertas, de um ou mais Fornecedores, que a gestora considera comparáveis entre si. Pode reunir itens iguais ou apenas semelhantes; o nome é dado pela gestora.
_Avoid_: Item, mercadoria, SKU, produto igual, produto semelhante

**Layout**:
A forma como um Catálogo organiza suas Ofertas na página. Um mesmo Fornecedor pode usar mais de um Layout.
_Avoid_: Formato, modelo

**Perfil do Fornecedor**:
Conjunto único de regras de um Fornecedor que os Catálogos não informam, definidas pela gestora e válidas para todas as Ofertas dele, como o Fracionamento e, para Catálogos em tabela, quais colunas são código, descrição, preço e Caixa.
_Avoid_: Cadastro, configuração

**Condições do Catálogo**:
Valores informados pela gestora a cada Importação, que valem só para aquele Catálogo e não alteram os preços impressos. Hoje, o desconto percentual além do que já está impresso (por exemplo, 3%), que não existe em Catálogos com várias colunas de preço, porque neles vale sempre a menor.
_Avoid_: Parâmetros, ajustes

### Preços e quantidades

**Unidade de venda**:
Aquilo que o preço impresso de uma Oferta compra: uma peça, um kit ou um jogo.
_Avoid_: Unidade, item

**Conteúdo**:
Quantos itens a loja vende separadamente a partir de uma Unidade de venda. É decisão da gestora, não do Catálogo: um kit com 3 tesouras vendidas avulsas tem Conteúdo 3; um kit de 13 peças vendido inteiro tem Conteúdo 1.
_Avoid_: Quantidade, quantidade por embalagem, peças no kit

**Caixa**:
Total de Unidades de venda que o Fornecedor entrega juntas. Não divide o preço: define a compra mínima quando não há Fracionamento.
_Avoid_: Fardo, master, embalagem

**Embalagem intermediária**:
Agrupamento de Unidades de venda dentro de uma Caixa, como dúzia, set ou sub-caixa. Assim como a Caixa, não divide o preço: "20 set" de 12 peças são 240 Unidades de venda na Caixa.
_Avoid_: Pacote, inner, display

**Fracionamento**:
Permissão de um Fornecedor para vender menos que uma Caixa, até uma menor quantidade definida no Perfil do Fornecedor.
_Avoid_: Caixa aberta, quebra de caixa

**Preço unitário**:
Preço impresso da Oferta, após o desconto percentual das Condições do Catálogo, dividido pelo Conteúdo: preço impresso × (1 − desconto%) ÷ Conteúdo, arredondado para centavos (meio centavo para cima). Não inclui impostos, que ficam com a contabilidade. É a base de toda comparação.
_Avoid_: Preço por embalagem, preço por caixa, custo

**Teto de compra**:
Maior Preço unitário que ainda permite revender com lucro. Hoje é um valor único para toda mercadoria, derivado do preço único de venda das lojas.
_Avoid_: Preço máximo, preço-alvo, limite

### Compras

**Gestor**:
Pessoa do grupo que compra para as próprias Lojas. Usa a base de compras comum do grupo, mas cada um tem seus próprios Pedidos.
_Avoid_: Usuário, comprador, sócio

**Loja**:
Unidade do grupo para a qual se compra mercadoria. Cada Loja pertence a um Gestor.
_Avoid_: Filial, unidade, empresa

**Representante**:
Intermediário que recebe, num único arquivo, os Pedidos de vários Fornecedores que representa. Não é um Fornecedor.
_Avoid_: Vendedor, distribuidor

**Pedido**:
Pedido de compra de um Gestor a um único Fornecedor, com Ofertas vigentes de qualquer Catálogo desse Fornecedor e a quantidade em Caixas destinada a cada uma das Lojas do Gestor. Não é venda: o sistema não tem dados de venda e não deve chamar um pelo outro.
_Avoid_: Venda, encomenda, compra

### Importação

**Importação**:
A entrada de um Catálogo no sistema, do envio do arquivo até a confirmação da Revisão.
_Avoid_: Upload, carga

**Revisão**:
Etapa da Importação em que a gestora confere, corrige e confirma as Ofertas extraídas. Nada é salvo sem ela.
_Avoid_: Validação, aprovação
