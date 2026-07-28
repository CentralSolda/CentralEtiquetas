from __future__ import annotations

from barcode import Code128
from barcode.writer import ImageWriter


def gerar_codigo_barras(valor: str):
    """Retorna uma instância Code128 para o valor informado."""
    return Code128(str(valor), writer=ImageWriter())
