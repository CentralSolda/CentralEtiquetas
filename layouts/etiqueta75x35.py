from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128
from reportlab.pdfbase.pdfmetrics import stringWidth

from utils.precos import formatar_brl


@dataclass(slots=True)
class Layout75x35:
    largura: float = 75 * mm
    altura: float = 35 * mm

    altura_cabecalho: float = 12 * mm
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
        self._desenhar_codigo_barras(c, x, y, produto)
        self._desenhar_sku(c, x, y, produto)

    def _desenhar_base(self, c, x, y):
        c.setFillColorRGB(*self.cor_branco)
        c.rect(x, y, self.largura, self.altura, fill=1, stroke=0)
        c.setStrokeColorRGB(*self.cor_azul)
        c.setLineWidth(0.5)
        c.rect(x, y, self.largura, self.altura, fill=0, stroke=1)

    def _desenhar_cabecalho(self, c, x, y):
        c.setFillColorRGB(*self.cor_azul)
        c.rect(x, y + 22.9 * mm, self.largura, self.altura_cabecalho, fill=1, stroke=0)
        c.setFillColorRGB(*self.cor_laranja)
        c.rect(x, y + 22.15 * mm, self.largura, 0.75 * mm, fill=1, stroke=0)
        c.rect(x, y + 22.9 * mm, 1.8 * mm, self.altura_cabecalho, fill=1, stroke=0)

    def _desenhar_logo(self, c, x, y, logo_reader: ImageReader):
        logo_x, logo_y = x + 2.5 * mm, y + 24.8 * mm
        c.setFillColorRGB(*self.cor_branco)
        c.roundRect(logo_x - 0.6 * mm, logo_y - 0.35 * mm, 31.8 * mm, 8.0 * mm, 1.3 * mm, fill=1, stroke=0)
        c.drawImage(logo_reader, logo_x, logo_y, width=30.5 * mm, height=7.0 * mm, preserveAspectRatio=True, mask="auto")

    def _desenhar_preco(self, c, x, y, produto: dict):
        valor = Decimal(str(produto.get("preco", "0")))
        preco = formatar_brl(valor)
        price_size = 20.0
        while price_size > 17 and stringWidth(preco, "Helvetica-Bold", price_size) > 37 * mm:
            price_size -= 0.4
        c.setFillColorRGB(*self.cor_branco)
        c.setFont("Helvetica-Bold", price_size)
        c.drawRightString(x + self.largura - 2.0 * mm, y + 27.1 * mm, preco)

    def _desenhar_descricao(self, c, x, y, produto: dict):
        descricao = str(produto.get("descricao", "")).strip()
        linhas, fs = self._quebrar_descricao(descricao, self.largura - 6 * mm)
        c.setFillColorRGB(*self.cor_azul)
        c.setFont("Helvetica-Bold", fs)
        first_y = y + (18.4 * mm if len(linhas) == 1 else 18.8 * mm)
        for idx, linha in enumerate(linhas[:2]):
            c.drawString(x + 2.8 * mm, first_y - idx * 3.0 * mm, linha)

        c.setFillColorRGB(*self.cor_laranja)
        c.roundRect(x + 2.8 * mm, y + 13.4 * mm, 11.5 * mm, 0.8 * mm, 0.4 * mm, fill=1, stroke=0)

    def _quebrar_descricao(self, texto: str, max_width: float):
        for size in [8.6, 8.4, 8.2, 8.0, 7.8, 7.6, 7.4, 7.2]:
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
        texto = texto[:30]
        return [texto], 7.2

    def _desenhar_codigo_barras(self, c, x, y, produto: dict):
        sku = str(produto.get("sku", "")).strip()
        base = code128.Code128(sku, barHeight=5.1 * mm, barWidth=0.48 * mm, humanReadable=False)
        scale = min(1.0, 62 * mm / base.width) if base.width else 1.0
        barcode = code128.Code128(sku, barHeight=5.1 * mm, barWidth=0.48 * mm * scale, humanReadable=False)
        c.setFillColorRGB(0, 0, 0)
        barcode.drawOn(c, x + (self.largura - barcode.width) / 2, y + 6.1 * mm)

    def _desenhar_sku(self, c, x, y, produto: dict):
        sku = str(produto.get("sku", "")).strip()
        capsule_w = max(20 * mm, stringWidth(sku, "Helvetica-Bold", 9.0) + 8 * mm)
        capsule_x = x + (self.largura - capsule_w) / 2
        c.setFillColorRGB(*self.cor_azul)
        c.roundRect(capsule_x, y + 1.0 * mm, capsule_w, 4.0 * mm, 1.8 * mm, fill=1, stroke=0)
        c.setFillColorRGB(*self.cor_branco)
        c.setFont("Helvetica-Bold", 9.0)
        c.drawCentredString(x + self.largura / 2, y + 2.05 * mm, sku)
