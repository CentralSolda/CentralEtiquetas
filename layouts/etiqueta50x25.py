from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from utils.precos import formatar_brl


@dataclass(slots=True)
class Layout50x25:
    largura: float = 50 * mm
    altura: float = 25 * mm

    altura_cabecalho: float = 10.7 * mm
    cor_azul = (5 / 255, 61 / 255, 112 / 255)
    cor_laranja = (1.0, 105 / 255, 0)
    cor_branco = (1, 1, 1)

    def desenhar(self, c, x: float, y: float, produto: dict, logo_reader: ImageReader | None = None):
        self._desenhar_base(c, x, y)
        self._desenhar_cabecalho(c, x, y)

        if logo_reader is not None:
            self._desenhar_logo(c, x, y, logo_reader)

        self._desenhar_preco(c, x, y, produto)
        self._desenhar_descricao(c, x, y, produto)
        self._desenhar_sku(c, x, y, produto)

    def _desenhar_base(self, c, x, y):
        c.setFillColorRGB(*self.cor_branco)
        c.rect(x, y, self.largura, self.altura, fill=1, stroke=0)
        c.setStrokeColorRGB(*self.cor_azul)
        c.setLineWidth(0.55)
        c.rect(x, y, self.largura, self.altura, fill=0, stroke=1)

    def _desenhar_cabecalho(self, c, x, y):
        c.setFillColorRGB(*self.cor_azul)
        c.rect(x, y + 14.3 * mm, self.largura, self.altura_cabecalho, fill=1, stroke=0)
        c.setFillColorRGB(*self.cor_laranja)
        c.rect(x, y + 13.55 * mm, self.largura, 0.75 * mm, fill=1, stroke=0)
        c.rect(x, y + 14.3 * mm, 1.25 * mm, self.altura_cabecalho, fill=1, stroke=0)

    def _desenhar_logo(self, c, x, y, logo_reader: ImageReader):
        logo_x, logo_y = x + 1.8 * mm, y + 16.6 * mm
        c.setFillColorRGB(*self.cor_branco)
        c.roundRect(logo_x - 0.45 * mm, logo_y - 0.35 * mm, 20.8 * mm, 6.4 * mm, 1.2 * mm, fill=1, stroke=0)
        c.drawImage(logo_reader, logo_x, logo_y, width=20.0 * mm, height=5.7 * mm, preserveAspectRatio=True, mask="auto")

    def _desenhar_preco(self, c, x, y, produto: dict):
        valor = Decimal(str(produto.get("preco", "0")))
        preco = formatar_brl(valor)
        price_size = 15.0
        while price_size > 10.5 and stringWidth(preco, "Helvetica-Bold", price_size) > 24 * mm:
            price_size -= 0.4
        c.setFillColorRGB(*self.cor_branco)
        c.setFont("Helvetica-Bold", price_size)
        c.drawRightString(x + self.largura - 1.2 * mm, y + 18.2 * mm, preco)

    def _desenhar_descricao(self, c, x, y, produto: dict):
        descricao = str(produto.get("descricao", "")).strip()
        linhas, fs = self._quebrar_descricao(descricao, self.largura - 4 * mm)
        c.setFillColorRGB(*self.cor_azul)
        c.setFont("Helvetica-Bold", fs)
        first_y = y + (8.3 * mm if len(linhas) == 1 else 10.2 * mm)
        for idx, linha in enumerate(linhas[:2]):
            c.drawString(x + 1.8 * mm, first_y - idx * 3.0 * mm, linha)

    def _quebrar_descricao(self, texto: str, max_width: float):
        for size in [7.0, 6.8, 6.6, 6.4, 6.2, 6.0, 5.8, 5.6]:
            words = texto.split()
            lines = [""]
            ok = True
            for word in words:
                trial = (lines[-1] + " " + word).strip()
                if stringWidth(trial, "Helvetica-Bold", size) <= max_width:
                    lines[-1] = trial
                elif len(lines) < 2:
                    lines.append(word)
                else:
                    ok = False
                    break
            if ok:
                return lines, size
        return [texto[:18] + ("..." if len(texto) > 18 else "")], 5.6

    def _desenhar_sku(self, c, x, y, produto: dict):
        sku = str(produto.get("sku", "")).strip()
        c.setFillColorRGB(*self.cor_azul)
        capsule_w = max(12 * mm, stringWidth(sku, "Helvetica-Bold", 8.0) + 5 * mm)
        capsule_x = x + (self.largura - capsule_w) / 2
        c.roundRect(capsule_x, y + 1.0 * mm, capsule_w, 3.6 * mm, 1.6 * mm, fill=1, stroke=0)
        c.setFillColorRGB(*self.cor_branco)
        c.setFont("Helvetica-Bold", 8.0)
        c.drawCentredString(x + self.largura / 2, y + 1.9 * mm, sku)
