import logging

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import select

from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.models.model_mydsystem.med_spdata_convenios_model import MedSpdataConvenio
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


def importar_convenios_spdata(batch_size=200):
    total_lidos = 0
    total_criados = 0
    total_atualizados = 0
    total_erros = 0

    sql = """
        SELECT
            COD,
            NOME,
            SITUACAO,
            REG_ANS
        FROM TBCONVEN
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
                        select(MedSpdataConvenio).where(
                            MedSpdataConvenio.codigo_spdata.in_(codigos_spdata)
                        )
                    ).scalars().all()

                existentes_por_codigo = {
                    convenio.codigo_spdata: convenio
                    for convenio in existentes
                }

                for row in rows:
                    total_lidos += 1

                    try:
                        dados = row_para_dict(row, nomes_colunas)
                        codigo_spdata = normalizar_int(dados.get("COD"))

                        if codigo_spdata is None:
                            total_erros += 1
                            logger.warning("Convênio ignorado sem COD. Linha: %s", total_lidos)
                            continue

                        nome = normalizar_texto(dados.get("NOME"), 255)
                        if not nome:
                            nome = f"Convênio SPDATA {codigo_spdata}"

                        convenio = existentes_por_codigo.get(codigo_spdata)
                        if convenio is None:
                            convenio = MedSpdataConvenio(codigo_spdata=codigo_spdata, nome=nome)
                            db.session.add(convenio)
                            existentes_por_codigo[codigo_spdata] = convenio
                            total_criados += 1
                        else:
                            total_atualizados += 1

                        convenio.nome = nome
                        convenio.situacao = normalizar_texto(dados.get("SITUACAO"), 50)
                        convenio.registro_ans = normalizar_texto(dados.get("REG_ANS"), 50)
                        convenio.dados_spdata = dados

                    except Exception:
                        total_erros += 1
                        logger.exception(
                            "Erro processando convênio SPDATA. Linha: %s",
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
        logger.exception("Falha na importação da TBCONVEN.")
        raise
