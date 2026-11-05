---
status: accepted, em parte substituído pelo ADR-0010 e pelo ADR-0011
---

> **Partes substituídas.** Pelo ADR-0010: "o arquivo de preços é o Catálogo", "documento sem preço continua não sendo importável" e "nesses Catálogos a Importação não pergunta desconto". Agora o desconto é sempre perguntado, por arquivo de preços, e um Catálogo sem preço é completado por planilhas de preços. Pelo ADR-0011: a foto deixa de ser só da grade de cartões. Os três caminhos e as regras de Revisão continuam valendo.

# Extração de catálogos em três caminhos, incluindo LLM com visão, sempre com Revisão

Substitui o ADR-0001. Numa amostra maior, com 30 arquivos de 13 fornecedores, apareceram planilhas Excel, tabelas com várias colunas de preço, catálogos de layout livre e catálogos em que preço e código existem só como imagem. A gestora confirmou que vários fornecedores mandam catálogos nesse último formato. Um leitor por Layout não alcança esses casos, e a digitação manual de dezenas de páginas inviabilizaria o uso. Decidimos extrair por três caminhos, escolhidos conforme o tipo de Catálogo:

1. **Grade de cartões** (PDF com texto, uma Oferta por cartão): leitor determinístico por Layout. O Layout é reconhecido automaticamente pelo conteúdo.
2. **Tabela** (Excel ou PDF com texto): um único leitor genérico. Na primeira Importação de cada Fornecedor, a gestora indica quais colunas são código, descrição, preço e Caixa. Esse mapeamento fica no Perfil do Fornecedor. Quando há mais de uma coluna de preço (por prazo, por desconto em cascata ou por faixa), vale **a menor de cada linha**. Nesses Catálogos a Importação não pergunta desconto, porque a menor coluna já é o preço final; perguntar levaria a aplicar o desconto duas vezes.
3. **Layout livre ou só imagem**: LLM com visão lê as páginas e propõe as Ofertas.

## Regras que valem para os três caminhos

- Nada é salvo sem a Revisão da gestora.
- Na Revisão, cada Oferta mostra de qual caminho veio. As Ofertas extraídas pela LLM aparecem ao lado da imagem da página de origem, para conferência visual.
- Ofertas com preço ausente, zero ou muito fora do padrão do próprio Catálogo ficam marcadas.
- Oferta sem Caixa (também chamada de fardo) não pode ser confirmada até a gestora informar a Caixa na Revisão.
- Ofertas cuja Unidade de venda é ambígua, como um kit vendido em set, ficam marcadas para a gestora conferir.
- Quando o caminho permite, a Revisão compara quantos preços havia no arquivo com quantas Ofertas foram extraídas.
- Um Catálogo pode chegar em dois arquivos, um com fotos e outro com preços. O arquivo de preços é o Catálogo; a foto da Oferta é opcional.
- Documento sem preço continua não sendo importável. Segundo a gestora, todo Fornecedor que manda catálogo só com fotos também manda uma tabela de preços.

## Opções consideradas

- **Só leitores por Layout (ADR-0001):** previsível e testável, mas deixa sem importação os catálogos só em imagem, que a gestora diz serem comuns.
- **LLM para tudo:** um caminho único, mas troca leituras determinísticas que já funcionam em grades e tabelas por uma leitura com custo por página e erros plausíveis.
- **Leitura de texto em imagem sem LLM:** mesmo com o texto lido, ainda faltaria entender a estrutura de um layout livre.

## Consequências

- Catálogos de layout livre ou só imagem são enviados a um serviço externo de LLM. A gestora autorizou esse envio: catálogos de fornecedor são material comercial, não dados pessoais.
- O critério principal para escolher o serviço de LLM é o menor custo, desde que ele leia imagem. A escolha concreta fica para o spec.
- Os testes automatizados não podem depender de respostas variáveis da LLM, nem de catálogos reais. Cada Layout e cada caminho são testados com um Catálogo fictício que imita a estrutura do real, sem copiar dados.
- Uma Oferta lida pela LLM pode trazer um preço errado que parece plausível. Por isso a conferência ao lado da imagem é obrigatória e não pode ser pulada em lote sem que a gestora veja as páginas.
