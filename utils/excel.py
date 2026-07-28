from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import csv
import pandas as pd


@dataclass(slots=True)
class Produto:
    sku: str
    descricao: str


def _normalizar_texto(valor: object) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def ler_produtos(caminho_arquivo: str | Path) -> list[Produto]:
    caminho = Path(caminho_arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    extensao = caminho.suffix.lower()
    if extensao == ".csv":
        return _ler_csv(caminho)
    if extensao in {".xlsx", ".xlsm"}:
        return _ler_excel(caminho)

    raise ValueError(f"Formato não suportado: {extensao}")


def _ler_csv(caminho: Path) -> list[Produto]:
    df = pd.read_csv(caminho, dtype=str, keep_default_na=False)
    return _df_para_produtos(df)


def _ler_excel(caminho: Path) -> list[Produto]:
    df = pd.read_excel(caminho, dtype=str).fillna("")
    return _df_para_produtos(df)


def _coluna_por_posicao(df: pd.DataFrame, index: int) -> str:
    if df.shape[1] <= index:
        raise ValueError(f"A planilha possui menos de {index + 1} colunas.")
    return df.columns[index]


def _df_para_produtos(df: pd.DataFrame) -> list[Produto]:
    if df.empty:
        raise ValueError("A planilha de produtos está vazia.")

    col_sku = _coluna_por_posicao(df, 1)  # coluna B
    col_descricao = _coluna_por_posicao(df, 2) if df.shape[1] > 2 else df.columns[0]

    produtos: list[Produto] = []
    for _, row in df.iterrows():
        sku = _normalizar_texto(row.get(col_sku, ""))
        descricao = _normalizar_texto(row.get(col_descricao, ""))

        if not sku or not descricao:
            continue
        if "caixa master" in descricao.lower():
            continue

        produtos.append(Produto(sku=sku, descricao=descricao))

    if not produtos:
        raise ValueError("Nenhum produto válido foi encontrado na planilha.")

    return produtos
