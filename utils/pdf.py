from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pdfplumber


def ler_tabela_precos(caminho_pdf: str | Path) -> dict[str, str]:
    """Lê a Tabela 1 e retorna um mapa SKU -> preço da lista (texto).

    A extração é feita de forma tolerante, buscando linhas com SKU e preço.
    """
    caminho = Path(caminho_pdf)
    if not caminho.exists():
        raise FileNotFoundError(f"PDF não encontrado: {caminho}")

    tabela: dict[str, str] = {}

    with pdfplumber.open(caminho) as pdf:
        for page in pdf.pages:
            texto = page.extract_text() or ""
            for linha in texto.splitlines():
                partes = [p for p in linha.split() if p]
                if len(partes) < 3:
                    continue

                sku = _identificar_sku(partes)
                preco = _identificar_preco(partes)
                if sku and preco:
                    tabela[sku] = preco

    if not tabela:
        raise ValueError("Não foi possível extrair preços da Tabela 1.")

    return tabela


def _identificar_sku(partes: list[str]) -> str | None:
    for item in partes:
        if item.isdigit() and 4 <= len(item) <= 8:
            return item
    return None


def _identificar_preco(partes: list[str]) -> str | None:
    for item in reversed(partes):
        if "," in item and any(ch.isdigit() for ch in item):
            texto = item.replace(".", "")
            if texto.count(",") == 1:
                antes, depois = texto.split(",")
                if antes.replace("-", "").isdigit() and depois.isdigit() and len(depois) == 2:
                    return texto
    return None
