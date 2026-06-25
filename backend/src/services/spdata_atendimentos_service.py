from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select

from src.models.anamnese_model import Anamnese
from src.models.atendimentos_model import Atendimento
from src.models.diagnostico_model import Diagnostico
from src.models.evolucoes_medicas_model import EvolucaoMedica
from src.models.medico_model import Medico
from src.models.model_mydsystem.med_atendimentos_model import (
    MedAtendimentos,
    StatusAtendimentoMedSystem,
)
from src.models.model_mydsystem.med_spdata_atendimentos_model import (
    MedSpdataAtendimento,
)
from src.models.prescricao_model import Prescricao
from src.models.solicitacao_exame_model import SolicitacaoExame
from src.models.db.handler_fb_db import ConnectionDBFireBird
from src.settings.extensions import db


UNIDADE_PADRAO_SPDATA = 203
DATA_OFFSET_HOMOLOGACAO_DIAS = 3

STATUS_VALIDOS = {
    "em-atendimento",
    "atendido",
    "faltou",
}

STATUS_ALIASES = {
    "EM_ATENDIMENTO": "em-atendimento",
    "em_atendimento": "em-atendimento",
    "em-atendimento": "em-atendimento",
    "ATENDIDO": "atendido",
    "atendido": "atendido",
    "FALTOU": "faltou",
    "faltou": "faltou",
}


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


def normalizar_data(valor):
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    return datetime.fromisoformat(str(valor)[:10]).date()


def normalizar_datetime(valor):
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor

    if isinstance(valor, date):
        return datetime.combine(valor, time.min)

    texto = str(valor).replace("Z", "")
    return datetime.fromisoformat(texto)


def normalizar_time(valor):
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.time().replace(microsecond=0)

    if isinstance(valor, time):
        return valor.replace(microsecond=0)

    texto = str(valor).strip()
    if len(texto) == 5:
        texto = f"{texto}:00"

    return time.fromisoformat(texto)


def normalizar_status(status):
    if status is None:
        return None

    return STATUS_ALIASES.get(str(status), str(status))


def row_para_dict(row, nomes_colunas):
    return {
        nome: normalizar_valor(valor)
        for nome, valor in zip(nomes_colunas, row)
    }


def get_crm_medico_usuario(usuario_id):
    medico = db.session.execute(
        select(Medico).where(
            Medico.usuario_id == usuario_id,
            Medico.ativo.is_(True),
        )
    ).scalars().first()

    crm_atendimento = normalizar_texto(
        getattr(medico, "crm_atendimento_spdata", None) if medico else None,
        50,
    )
    crm = normalizar_texto(medico.crm, 50) if medico else None

    if not medico or not (crm_atendimento or crm):
        raise ValueError("Médico local não possui crm_atendimento_spdata nem crm configurado para filtrar o SPDATA.")

    return crm_atendimento or crm


def buscar_atendimentos_spdata(data_ini, data_fim, crm_medico):
    sql = """
        SELECT
            a.ID AS SPDATA_ATENDIMENTO_ID,
            a.COD_ATENDIMENTO,
            a.ID_RICADPAC AS ID_PACIENTE_SPDATA,
            a.DATA_HORA_ENTRADA,
            a.DATA_HORA_ALTA_MEDICA,
            a.OBS_ATENDIMENTO,
            a.ID_TBCONVEN AS ID_CONVENIO_SPDATA,
            a.ID_TBCENCUS AS ID_CENTRO_CUSTO_SPDATA,

            paciente.PRONT AS PRONTUARIO,
            paciente.NOME AS PACIENTE,
            paciente.NASC AS DATA_NASCIMENTO,
            paciente.SEXO AS SEXO,
            paciente.CELULAR AS CELULAR,
            paciente.EMAIL AS EMAIL,
            paciente.CPF AS CPF,
            paciente.ENDERECO AS ENDERECO,

            medico.ID AS ID_MEDICO_SPDATA,
            medico.NOME AS MEDICO,
            tb.COD AS CRM_MEDICO
        FROM ATCABECATEND a
        INNER JOIN RICADPAC paciente
            ON paciente.ID = a.ID_RICADPAC
        INNER JOIN TBCBOPRO tb
            ON a.ID_TBCBOPRO_ATENDIMENTO = tb.ID
        INNER JOIN TBPROFIS medico
            ON tb.ID_TBPROFIS = medico.ID
        WHERE a.ID_TBCENCUS = ?
          AND tb.COD = ?
          AND CAST(a.DATA_HORA_ENTRADA AS DATE) = CURRENT_DATE - 3
        ORDER BY a.DATA_HORA_ENTRADA, paciente.NOME;
    """

    with ConnectionDBFireBird() as connection:
        cursor = connection.cursor()
        cursor.execute(
            sql,
            (
                UNIDADE_PADRAO_SPDATA,
                crm_medico,
            ),
        )
        nomes_colunas = [descricao[0].strip().upper() for descricao in cursor.description]
        return [row_para_dict(row, nomes_colunas) for row in cursor.fetchall()]


def sincronizar_atendimentos_spdata(data_ini, data_fim, crm_medico):
    dados_spdata = buscar_atendimentos_spdata(data_ini, data_fim, crm_medico)
    ids_spdata = [
        normalizar_int(item.get("SPDATA_ATENDIMENTO_ID"))
        for item in dados_spdata
        if item.get("SPDATA_ATENDIMENTO_ID") is not None
    ]

    existentes = {}
    if ids_spdata:
        registros = db.session.execute(
            select(MedSpdataAtendimento).where(
                MedSpdataAtendimento.spdata_atendimento_id.in_(ids_spdata)
            )
        ).scalars().all()
        existentes = {registro.spdata_atendimento_id: registro for registro in registros}

    total_criados = 0
    total_atualizados = 0

    for item in dados_spdata:
        spdata_atendimento_id = normalizar_int(item.get("SPDATA_ATENDIMENTO_ID"))
        data_hora_entrada = normalizar_datetime(item.get("DATA_HORA_ENTRADA"))
        paciente = normalizar_texto(item.get("PACIENTE"), 255)

        if not spdata_atendimento_id or not data_hora_entrada or not paciente:
            continue

        registro = existentes.get(spdata_atendimento_id)
        if registro is None:
            registro = MedSpdataAtendimento(
                spdata_atendimento_id=spdata_atendimento_id,
                data_hora_entrada=data_hora_entrada,
                data_atendimento=data_hora_entrada.date(),
                paciente=paciente,
            )
            db.session.add(registro)
            existentes[spdata_atendimento_id] = registro
            total_criados += 1
        else:
            total_atualizados += 1

        registro.cod_atendimento = normalizar_texto(item.get("COD_ATENDIMENTO"), 50)
        registro.id_paciente_spdata = normalizar_int(item.get("ID_PACIENTE_SPDATA"))
        registro.id_medico_spdata = normalizar_int(item.get("ID_MEDICO_SPDATA"))
        registro.medico = normalizar_texto(item.get("MEDICO"), 255)
        registro.crm_medico = normalizar_texto(item.get("CRM_MEDICO"), 50)
        registro.data_hora_entrada = data_hora_entrada
        registro.data_atendimento = data_hora_entrada.date()
        registro.hora_entrada = data_hora_entrada.time().replace(microsecond=0)
        registro.data_hora_alta_medica = normalizar_datetime(item.get("DATA_HORA_ALTA_MEDICA"))
        registro.id_convenio_spdata = normalizar_int(item.get("ID_CONVENIO_SPDATA"))
        registro.id_centro_custo_spdata = normalizar_int(item.get("ID_CENTRO_CUSTO_SPDATA"))
        registro.obs_atendimento = normalizar_texto(item.get("OBS_ATENDIMENTO"))
        registro.paciente = paciente
        registro.cpf = normalizar_texto(item.get("CPF"), 20)
        registro.prontuario = normalizar_texto(item.get("PRONTUARIO"), 50)
        registro.data_nascimento = normalizar_data(item.get("DATA_NASCIMENTO"))
        registro.sexo = normalizar_texto(item.get("SEXO"), 20)
        registro.celular = normalizar_texto(item.get("CELULAR"), 30)
        registro.email = normalizar_texto(item.get("EMAIL"), 255)
        registro.endereco = normalizar_texto(item.get("ENDERECO"), 500)
        registro.dados_spdata = item

    db.session.commit()

    return {
        "lidos": len(dados_spdata),
        "criados": total_criados,
        "atualizados": total_atualizados,
    }


def sexo_para_frontend(sexo):
    return "feminino" if str(sexo or "").upper().startswith("F") else "masculino"


def data_iso(valor):
    return valor.isoformat() if valor else None


def hora_hhmm(valor):
    return valor.strftime("%H:%M") if valor else ""


def agenda_para_frontend(spdata, atendimento=None):
    status = normalizar_status(atendimento.status) if atendimento else "em-espera"
    data_atendimento = data_iso(spdata.data_atendimento)
    horario = hora_hhmm(spdata.hora_entrada)
    paciente_id = spdata.id_paciente_spdata or spdata.id

    return {
        "id": spdata.id,
        "spdataAtendimentoId": spdata.spdata_atendimento_id,
        "codAtendimento": spdata.cod_atendimento,
        "medsystemAtendimentoId": atendimento.id if atendimento else None,
        "pacienteId": paciente_id,
        "medicoId": spdata.id_medico_spdata or 0,
        "clinicaId": 1,
        "data": data_atendimento,
        "horario": horario,
        "prioridade": "normal",
        "status": status,
        "descricao": spdata.obs_atendimento or "",
        "criadoEm": spdata.data_hora_entrada.isoformat() if spdata.data_hora_entrada else None,
        "paciente": {
            "id": paciente_id,
            "nome": spdata.paciente,
            "encaixado": False,
            "sexo": sexo_para_frontend(spdata.sexo),
            "dataNascimento": data_iso(spdata.data_nascimento) or "1900-01-01",
            "tipoSanguineo": "",
            "alergias": [],
            "medicamentosEmUso": [],
            "convenio": str(spdata.id_convenio_spdata or ""),
            "telefone": spdata.celular or "",
            "email": spdata.email or "Não Informado",
            "cpf": spdata.cpf or "",
            "endereco": spdata.endereco or "",
            "historicoRecente": [],
        },
    }


def listar_agenda_medica(usuario_id, data_ini, data_fim):
    crm_medico = get_crm_medico_usuario(usuario_id)
    data_homologacao = date.today() - timedelta(days=DATA_OFFSET_HOMOLOGACAO_DIAS)
    sincronizar_atendimentos_spdata(data_homologacao, data_homologacao, crm_medico)

    registros = (
        db.session.query(MedSpdataAtendimento, MedAtendimentos)
        .outerjoin(
            MedAtendimentos,
            MedAtendimentos.med_spdata_atendimento_id == MedSpdataAtendimento.id,
        )
        .filter(
            MedSpdataAtendimento.data_atendimento == data_homologacao,
            MedSpdataAtendimento.crm_medico == crm_medico,
            MedSpdataAtendimento.id_centro_custo_spdata == UNIDADE_PADRAO_SPDATA,
        )
        .order_by(MedSpdataAtendimento.data_hora_entrada, MedSpdataAtendimento.paciente)
        .all()
    )

    return [agenda_para_frontend(spdata, atendimento) for spdata, atendimento in registros]


def linhas_texto(valor):
    if not valor:
        return []

    linhas = []
    for linha in str(valor).splitlines():
        texto = linha.strip().lstrip("•- ").strip()
        if texto:
            linhas.append(texto)

    return linhas


def salvar_conteudo_clinico(spdata, atendimento_medsystem, usuario_id, consulta):
    if not consulta:
        return

    atendimento = db.session.execute(
        select(Atendimento).where(
            Atendimento.spdata_atendimento_id == spdata.spdata_atendimento_id
        )
    ).scalars().first()

    hora_inicio = (
        atendimento_medsystem.started_at.time().replace(microsecond=0)
        if atendimento_medsystem.started_at
        else spdata.hora_entrada
    )
    hora_fim = datetime.utcnow().time().replace(microsecond=0)

    if atendimento is None:
        atendimento = Atendimento(
            spdata_paciente_id=spdata.id_paciente_spdata,
            spdata_agenda_id=None,
            spdata_medico_id=spdata.id_medico_spdata,
            paciente_nome=spdata.paciente,
            paciente_cpf=spdata.cpf or "",
            data_atendimento=spdata.data_hora_entrada,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            spdata_atendimento_id=spdata.spdata_atendimento_id,
        )
        db.session.add(atendimento)
        db.session.flush()
        atendimento.status = "finalizado"
    else:
        atendimento.hora_fim = hora_fim
        atendimento.status = "finalizado"

    anamnese_texto = normalizar_texto(consulta.get("anamnese"))
    if anamnese_texto:
        if atendimento.anamnese:
            atendimento.anamnese.observacoes = anamnese_texto
        else:
            db.session.add(Anamnese(atendimento_id=atendimento.id, observacoes=anamnese_texto))

        evolucao = atendimento.evolucoes_medicas[0] if atendimento.evolucoes_medicas else None
        if evolucao:
            evolucao.texto_evolucao = anamnese_texto
            evolucao.status = "finalizado"
        else:
            db.session.add(
                EvolucaoMedica(
                    atendimento_id=atendimento.id,
                    medico_id=usuario_id,
                    texto_evolucao=anamnese_texto,
                    status="finalizado",
                )
            )

    diagnostico = normalizar_texto(consulta.get("diagnostico"), 255)
    if diagnostico:
        diagnostico_existente = atendimento.diagnosticos[0] if atendimento.diagnosticos else None
        if diagnostico_existente:
            diagnostico_existente.cid_codigo = diagnostico
            diagnostico_existente.diagnostico_descritivo = diagnostico
            diagnostico_existente.principal = True
        else:
            db.session.add(
                Diagnostico(
                    atendimento_id=atendimento.id,
                    cid_codigo=diagnostico,
                    diagnostico_descritivo=diagnostico,
                    principal=True,
                )
            )

    if "medicamentos" in consulta:
        for prescricao in list(atendimento.prescricoes):
            db.session.delete(prescricao)

        for linha in linhas_texto(consulta.get("medicamentos")):
            nome, separador, dosagem = linha.partition("—")
            db.session.add(
                Prescricao(
                    atendimento_id=atendimento.id,
                    medico_id=usuario_id,
                    medicamento=normalizar_texto(nome, 255) or linha[:255],
                    dosagem=normalizar_texto(dosagem, 100) if separador else None,
                    orientacoes=linha,
                )
            )

    if "exames" in consulta:
        for solicitacao in list(atendimento.solicitacoes_exames):
            db.session.delete(solicitacao)

        for linha in linhas_texto(consulta.get("exames")):
            db.session.add(
                SolicitacaoExame(
                    atendimento_id=atendimento.id,
                    tipo_exame=normalizar_texto(linha, 255) or linha[:255],
                    descricao=linha,
                )
            )


def atualizar_status_agenda(med_spdata_atendimento_id, status, usuario_id=None, consulta=None):
    status = normalizar_status(status)
    if status not in STATUS_VALIDOS:
        raise ValueError("Status inválido")

    spdata = db.session.get(MedSpdataAtendimento, med_spdata_atendimento_id)
    if not spdata:
        raise LookupError("Atendimento do SPDATA não encontrado no MedSystem")

    atendimento = db.session.execute(
        select(MedAtendimentos).where(
            MedAtendimentos.med_spdata_atendimento_id == spdata.id
        )
    ).scalars().first()

    if atendimento is None:
        atendimento = MedAtendimentos(
            med_spdata_atendimento_id=spdata.id,
            spdata_atendimento_id=spdata.spdata_atendimento_id,
            cod_atendimento=spdata.cod_atendimento,
            data_agenda=spdata.data_atendimento,
            hora_agenda=spdata.hora_entrada,
            id_medico_spdata=spdata.id_medico_spdata,
            medico=spdata.medico,
            id_paciente_spdata=spdata.id_paciente_spdata,
            paciente=spdata.paciente,
            cpf=spdata.cpf,
            prontuario=spdata.prontuario,
        )
        db.session.add(atendimento)

    if status == "em-atendimento":
        atendimento.marcar_em_atendimento()
    elif status == "atendido":
        atendimento.marcar_atendido()
        salvar_conteudo_clinico(spdata, atendimento, usuario_id, consulta)
    elif status == "faltou":
        atendimento.marcar_faltou()

    db.session.commit()
    return agenda_para_frontend(spdata, atendimento)
