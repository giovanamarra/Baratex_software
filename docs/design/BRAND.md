# Identidade visual da Baratex

Fonte: `assets/BARATEX - Sua Marca (1).pdf.pdf` (brandbook). Toda tela HTML, template Django, CSS ou e-mail gerado neste projeto segue este arquivo. Não invente cores, fontes ou variações de logo fora daqui.

## Cores

Cores da marca (do manual):

| Token | Hex | Uso |
|---|---|---|
| `--bx-verde` | `#003D1E` | Cor principal. Cabeçalho, barra de navegação, botão primário, títulos e texto principal em fundo claro |
| `--bx-limao` | `#9CFF00` | Destaque. Só sobre verde ou como preenchimento (borda, faixa, selo, foco), **nunca como cor de texto em fundo claro** |
| `--bx-cinza` | `#EFEFEF` | Fundo das páginas |
| `--bx-preto` | `#1D1D1B` | Uso raro (versão do logo em fundo preto) |

Derivadas para a interface (não estão no manual; mantêm o contraste mínimo WCAG AA de 4,5:1 para texto):

| Token | Hex | Uso |
|---|---|---|
| `--bx-branco` | `#FFFFFF` | Fundo de cartões, tabelas e formulários |
| `--bx-verde-2` | `#0B5230` | Hover do botão primário, cartões sobre fundo verde |
| `--bx-verde-texto` | `#2E7D00` | Texto de destaque e links em fundo claro |
| `--bx-texto-2` | `#3F5246` | Texto secundário em fundo claro |
| `--bx-texto-claro` | `#C7D8CB` | Texto secundário em fundo verde |
| `--bx-borda` | `#D8DCD5` | Bordas e divisórias |
| `--bx-limao-claro` | `#E3FFB8` | Linha selecionada numa tabela. Nunca para destacar a "melhor" Oferta: o sistema não elege vencedora (ADR-0003) |
| `--bx-erro` | `#B3261E` | Erros de regra de negócio e recusas |
| `--bx-alerta-fundo` / `--bx-alerta` | `#FFF4D6` / `#7A4F00` | Marcas de conferência na Revisão e alerta de Teto de compra |

Regras:

- Botão primário: fundo `--bx-verde`, texto branco; foco com contorno de 3px `--bx-limao`.
- Botão secundário: fundo branco, borda e texto `--bx-verde`.
- Cor nunca é o único sinal: alerta de Teto, erro e marcas de conferência levam também ícone ou texto ("acima do Teto").
- Tabelas: cabeçalho `--bx-verde` com texto branco, linhas alternando branco e `--bx-cinza`.

## Tipografia

- O manual usa **Acumin Variable Concept** (Adobe, paga). Enquanto não houver licença e arquivo da fonte no projeto, use **Archivo** (Google Fonts), com `Arial, sans-serif` de reserva.
- Pesos: 400 texto, 600 rótulos, 700 títulos.
- Números e preços: `font-variant-numeric: tabular-nums`, para as colunas de Preço unitário alinharem.

## Logo

Arquivos em `assets/`:

- `logo-baratex-contorno.png`: contorno limão, para fundo `--bx-verde`. É o logo da barra de navegação.
- `logo-baratex-etiqueta.png`: etiqueta preenchida, para fundos claros.

Não recolorir, distorcer nem recriar o logo em CSS ou SVG. Altura mínima de 32px.

## Tokens CSS

O primeiro ticket com HTML cria `static/css/tokens.css` com este conteúdo, e o resto do CSS usa só as variáveis:

```css
:root {
  --bx-verde: #003D1E;
  --bx-limao: #9CFF00;
  --bx-cinza: #EFEFEF;
  --bx-preto: #1D1D1B;
  --bx-branco: #FFFFFF;
  --bx-verde-2: #0B5230;
  --bx-verde-texto: #2E7D00;
  --bx-texto-2: #3F5246;
  --bx-texto-claro: #C7D8CB;
  --bx-borda: #D8DCD5;
  --bx-limao-claro: #E3FFB8;
  --bx-erro: #B3261E;
  --bx-alerta-fundo: #FFF4D6;
  --bx-alerta: #7A4F00;
  --bx-fonte: "Archivo", Arial, sans-serif;
  --bx-raio: 12px;
}
```
