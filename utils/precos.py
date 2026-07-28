from __future__ import annotations

from decimal import Decimal, ROUND_FLOOR


def arredondar_preco(valor: float | int | str | Decimal) -> Decimal:
    """Arredonda para finais .00, .50, .90 ou .99.

    Regras:
    - 0,00 permanece 0,00
    - 0,01 até 0,50 -> 0,50
    - 0,51 até 0,90 -> 0,90
    - 0,91 até 0,99 -> 0,99
    """
    valor = Decimal(str(valor)).quantize(Decimal("0.01"))
    inteiro = valor.to_integral_value(rounding=ROUND_FLOOR)
    centavos = valor - inteiro

    if centavos == Decimal("0.00"):
        return valor
    if centavos <= Decimal("0.50"):
        return inteiro + Decimal("0.50")
    if centavos <= Decimal("0.90"):
        return inteiro + Decimal("0.90")
    return inteiro + Decimal("0.99")


def formatar_brl(valor: float | int | str | Decimal) -> str:
    preco = Decimal(str(valor)).quantize(Decimal("0.01"))
    texto = f"{preco:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")
