from datetime import date, datetime
import re


def _only_digits(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\D", "", value)


def format_cpf_or_cnpj(document: str | None) -> str | None:
    """
    Formata CPF/CNPJ:
      - 11 dígitos -> 000.000.000-00
      - 14 dígitos -> 00.000.000/0000-00
    Qualquer outro tamanho: retorna o valor original.
    """
    if document is None:
        return None

    digits = _only_digits(document)

    if len(digits) == 11:  # CPF
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

    if len(digits) == 14:  # CNPJ
        return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"

    # tamanho inválido -> devolve original (ou você pode levantar erro se quiser)
    return document


def format_cep(cep: str | None) -> str | None:
    """
    Formata CEP:
      - 8 dígitos -> 00000-000
    Qualquer outro tamanho: retorna o valor original.
    """
    if cep is None:
        return None

    digits = _only_digits(cep)

    if len(digits) == 8:
        return f"{digits[0:5]}-{digits[5:8]}"

    return cep


def format_to_br_date(d: datetime | date | None) -> str:
    if not d:
        return ""
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime("%d/%m/%Y")


def replace_empty_strings_with_none(value):
    if isinstance(value, dict):
        return {k: replace_empty_strings_with_none(v) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_empty_strings_with_none(v) for v in value]
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def capitalize_first_of_all(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())
