# CentralEtiquetas

Gerador de etiquetas para a Central Solda.

## O que o programa faz
- Lê uma lista de produtos em CSV, XLSX ou XLSM
- Usa o SKU da coluna B
- Lê a Tabela 1 em PDF
- Cruzamento por SKU
- Aplica o arredondamento padrão:
  - 0,00 permanece 0,00
  - 0,01 a 0,50 -> 0,50
  - 0,51 a 0,90 -> 0,90
  - 0,91 a 0,99 -> 0,99
- Gera PDF A4 com etiquetas

## Modelos disponíveis
- 75 x 35 mm
- 75 x 25 mm
- 50 x 25 mm

## Como usar
1. Abra o `main.py`
2. Selecione a lista de produtos
3. Selecione a Tabela 1 em PDF
4. Escolha o modelo
5. Clique em **GERAR ETIQUETAS**

## Saída
Os PDFs são salvos na pasta `output/`.
