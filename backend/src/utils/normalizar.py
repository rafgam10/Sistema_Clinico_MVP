import re


def normalizar_cpf(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto_sem_decimal = texto[:-2]
        if len(re.sub(r"\D", "", texto_sem_decimal)) == 11:
            texto = texto_sem_decimal

    cpf = re.sub(r"\D", "", texto)
    if len(cpf) != 11:
        return None
    if len(set(cpf)) == 1:
        return None

    return cpf
