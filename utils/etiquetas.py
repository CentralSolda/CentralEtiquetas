from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from layouts.etiqueta75x35 import Layout75x35
from utils.precos import arredondar_preco, formatar_brl


@dataclass(slots=True)
class ResultadoGeracao:
    arquivo_pdf: str
    total_produtos: int
    total_etiquetas: int
    paginas: int


class GeradorEtiquetas:
    def __init__(self, logo_path: str | None = None):
        self.logo_reader = ImageReader(logo_path) if logo_path and Path(logo_path).exists() else None

    def gerar_pdf(self, produtos: list[dict], caminho_saida: str, modelo: str = "75x35") -> ResultadoGeracao:
        if modelo != "75x35":
            raise NotImplementedError("Somente o layout 75x35 está implementado nesta etapa.")

        layout = Layout75x35()
        c = canvas.Canvas(caminho_saida, pagesize=A4)

        cols = 2
        rows = 8
        etiquetas_por_pagina = cols * rows
        page_w, page_h = A4
        left = (page_w - cols * layout.largura) / 2
        bottom = (page_h - rows * layout.altura) / 2

        total_etiquetas = 0
        for idx, produto in enumerate(produtos):
            if idx and idx % etiquetas_por_pagina == 0:
                c.showPage()
            pos = idx % etiquetas_por_pagina
            col = pos % cols
            row = pos // cols
            x = left + col * layout.largura
            y = page_h - bottom - (row + 1) * layout.altura
            layout.desenhar(c, x, y, produto, self.logo_reader)
            total_etiquetas += 1

        c.save()
        paginas = max(1, (total_etiquetas + etiquetas_por_pagina - 1) // etiquetas_por_pagina)
        return ResultadoGeracao(
            arquivo_pdf=str(caminho_saida),
            total_produtos=len(produtos),
            total_etiquetas=total_etiquetas,
            paginas=paginas,
        )
