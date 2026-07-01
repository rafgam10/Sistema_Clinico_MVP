import logging

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import select

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.model_mydsystem.med_spdata_especialidades_model import (
    MedSpdataEspecialidade,
)
from src.settings.extensions import db


logger = logging.getLogger(__name__)


def normalizar_valor(valor):
    if valor is None:
        return None
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    if isinstance(valor, bytes):
        try:
            return valor.decode("utf-8")
        except UnicodeDecodeError:
            return valor.hex()
    if hasattr(valor, "read"):
        conteudo = valor.read()
        if isinstance(conteudo, bytes):
            try:
                return conteudo.decode("utf-8")
            except UnicodeDecodeError:
                return conteudo.hex()
        return str(conteudo)
    return valor


def normalizar_texto(valor, limite=None):
    if valor is None:
        return None

    valor = str(valor).strip()
    if limite:
        valor = valor[:limite]

    return valor or None


def normalizar_int(valor):
    if valor is None or valor == "":
        return None

    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def row_para_dict(row, nomes_colunas):
    return {
        nome: normalizar_valor(valor)
        for nome, valor in zip(nomes_colunas, row)
    }


def importar_especialidades_spdata(batch_size=200):
    total_lidos = 0
    total_criados = 0
    total_atualizados = 0
    total_erros = 0

    sql = """
        SELECT
            COD,
            NOME,
            CRED,
            REFEXP,
            SIGLA,
            IDADE_INICIAL,
            IDADE_FINAL,
            SEXO,
            ID_TBDIGITAL_ESPECIALIDADE
        FROM TBESPEC
        ORDER BY NOME
    """

    try:
        with ConnectionDBFireBird() as connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            nomes_colunas = [desc[0].strip().upper() for desc in cursor.description]

            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break

                codigos_spdata = [
                    normalizar_int(row[0])
                    for row in rows
                    if normalizar_int(row[0]) is not None
                ]

                existentes = []
                if codigos_spdata:
                    existentes = db.session.execute(
                        select(MedSpdataEspecialidade).where(
                            MedSpdataEspecialidade.codigo_spdata.in_(codigos_spdata)
                        )
                    ).scalars().all()

                existentes_por_codigo = {
                    especialidade.codigo_spdata: especialidade
                    for especialidade in existentes
                }

                for row in rows:
                    total_lidos += 1

                    try:
                        dados = row_para_dict(row, nomes_colunas)
                        codigo_spdata = normalizar_int(dados.get("COD"))

                        if codigo_spdata is None:
                            total_erros += 1
                            logger.warning(
                                "Especialidade ignorada sem COD. Linha: %s",
                                total_lidos,
                            )
                            continue

                        nome = normalizar_texto(dados.get("NOME"), 255)
                        if not nome:
                            nome = f"Especialidade SPDATA {codigo_spdata}"

                        especialidade = existentes_por_codigo.get(codigo_spdata)
                        if especialidade is None:
                            especialidade = MedSpdataEspecialidade(
                                codigo_spdata=codigo_spdata,
                                nome=nome,
                            )
                            db.session.add(especialidade)
                            existentes_por_codigo[codigo_spdata] = especialidade
                            total_criados += 1
                        else:
                            total_atualizados += 1

                        especialidade.nome = nome
                        especialidade.cred = normalizar_texto(dados.get("CRED"), 50)
                        especialidade.refexp = normalizar_texto(dados.get("REFEXP"), 50)
                        especialidade.sigla = normalizar_texto(dados.get("SIGLA"), 50)
                        especialidade.idade_inicial = normalizar_int(
                            dados.get("IDADE_INICIAL")
                        )
                        especialidade.idade_final = normalizar_int(
                            dados.get("IDADE_FINAL")
                        )
                        especialidade.sexo = normalizar_texto(dados.get("SEXO"), 20)
                        especialidade.id_tbdigital_especialidade = normalizar_int(
                            dados.get("ID_TBDIGITAL_ESPECIALIDADE")
                        )
                        especialidade.dados_spdata = dados

                    except Exception:
                        total_erros += 1
                        logger.exception(
                            "Erro processando especialidade SPDATA. Linha: %s",
                            total_lidos,
                        )

                db.session.commit()

        return {
            "lidos": total_lidos,
            "criados": total_criados,
            "atualizados": total_atualizados,
            "erros": total_erros,
        }

    except Exception:
        db.session.rollback()
        logger.exception("Falha na importação da TBESPEC.")
        raise
