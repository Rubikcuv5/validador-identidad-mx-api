import re
from datetime import date

# CURP: 4 letras, 6 dígitos fecha, sexo, estado, 3 consonantes internas, homoclave, dígito verificador
_CURP_RE = re.compile(r"^[A-Z]{4}\d{6}[HM][A-Z]{2}[B-DF-HJ-NP-TV-Z]{3}[A-Z0-9]\d$")

# Tabla de caracteres para dígito verificador CURP
_CURP_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _curp_check_digit(curp17: str) -> str:
    """Calcula el dígito verificador de los primeros 17 caracteres."""
    total = sum((18 - i) * _CURP_CHARS.index(c) for i, c in enumerate(curp17))
    remainder = total % 10
    return str(0 if remainder == 0 else 10 - remainder)


def validate_curp(curp: str) -> dict:
    curp = curp.upper().strip()
    if not _CURP_RE.match(curp):
        return {"valid": False, "reason": "Formato inválido", "type": "CURP", "value": curp}

    expected = _curp_check_digit(curp[:17])
    if curp[17] != expected:
        return {
            "valid": False,
            "reason": f"Dígito verificador incorrecto (esperado {expected})",
            "type": "CURP",
            "value": curp,
        }

    return {"valid": True, "reason": "OK", "type": "CURP", "value": curp}


# RFC: 3-4 letras (personas morales 3, físicas 4), 6 dígitos fecha, 3 homoclave
_RFC_RE = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")


def validate_rfc(rfc: str) -> dict:
    rfc = rfc.upper().strip()
    if not _RFC_RE.match(rfc):
        return {"valid": False, "reason": "Formato inválido", "type": "RFC", "value": rfc}

    # Extraer fecha: posición 3 o 4 dependiendo de longitud
    offset = 4 if len(rfc) == 13 else 3
    date_str = rfc[offset : offset + 6]
    yy, mm, dd = int(date_str[:2]), int(date_str[2:4]), int(date_str[4:6])
    year = 2000 + yy if yy <= 30 else 1900 + yy

    try:
        date(year, mm, dd)
    except ValueError:
        return {
            "valid": False,
            "reason": f"Fecha imposible: {dd}/{mm}/{year}",
            "type": "RFC",
            "value": rfc,
        }

    return {"valid": True, "reason": "OK", "type": "RFC", "value": rfc}
