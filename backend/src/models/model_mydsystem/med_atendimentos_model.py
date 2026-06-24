from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLEnum

from src.settings.extensions import db


class StatusAtendimentoMedSystem(Enum):
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    ATENDIDO = "ATENDIDO"
    FALTOU = "FALTOU"


class MedAtendimentos(db.Model):
    __tablename__ = "MED_ATENDIMENTOS"

    id = db.Column(db.Integer, primary_key=True)

    spdata_agenda_id = db.Column(
        db.Integer,
        db.ForeignKey("MED_SPDATA_AGENDA.spdata_agenda_id"),
        nullable=False,
        index=True
    )

    id_medico_spdata = db.Column(db.Integer, nullable=True, index=True)
    medico = db.Column(db.String(255), nullable=True)

    data_agenda = db.Column(db.Date, nullable=False, index=True)
    hora_agenda = db.Column(db.Time, nullable=True)

    id_paciente_spdata = db.Column(db.Integer, nullable=True, index=True)
    paciente = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(20), nullable=True, index=True)
    prontuario = db.Column(db.String(50), nullable=True, index=True)

    status = db.Column(
        SQLEnum(StatusAtendimentoMedSystem, name="status_atendimento_medsystem"),
        nullable=False,
        default=StatusAtendimentoMedSystem.EM_ATENDIMENTO,
        index=True
    )

    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    finished_at = db.Column(db.DateTime, nullable=True)
    faltou_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    agenda = db.relationship(
        "MedSpdataAgenda",
        back_populates="atendimentos"
    )

    def __init__(
        self,
        spdata_agenda_id,
        data_agenda,
        paciente,
        status=StatusAtendimentoMedSystem.EM_ATENDIMENTO,
        id_medico_spdata=None,
        medico=None,
        hora_agenda=None,
        id_paciente_spdata=None,
        cpf=None,
        prontuario=None,
        started_at=None,
        finished_at=None,
        faltou_at=None
    ):
        self.spdata_agenda_id = spdata_agenda_id
        self.id_medico_spdata = id_medico_spdata
        self.medico = medico
        self.data_agenda = data_agenda
        self.hora_agenda = hora_agenda
        self.id_paciente_spdata = id_paciente_spdata
        self.paciente = paciente
        self.cpf = cpf
        self.prontuario = prontuario
        self.status = status
        self.started_at = started_at or datetime.utcnow()
        self.finished_at = finished_at
        self.faltou_at = faltou_at

    def marcar_em_atendimento(self):
        self.status = StatusAtendimentoMedSystem.EM_ATENDIMENTO
        self.started_at = self.started_at or datetime.utcnow()
        self.finished_at = None
        self.faltou_at = None

    def marcar_atendido(self):
        self.status = StatusAtendimentoMedSystem.ATENDIDO
        self.finished_at = datetime.utcnow()

    def marcar_faltou(self):
        self.status = StatusAtendimentoMedSystem.FALTOU
        self.faltou_at = datetime.utcnow()

    def _to_dict(self):
        status = self.status.value if hasattr(self.status, "value") else self.status

        return {
            "id": self.id,
            "spdata_agenda_id": self.spdata_agenda_id,
            "id_medico_spdata": self.id_medico_spdata,
            "medico": self.medico,
            "data_agenda": self.data_agenda.isoformat() if self.data_agenda else None,
            "hora_agenda": str(self.hora_agenda) if self.hora_agenda else None,
            "id_paciente_spdata": self.id_paciente_spdata,
            "paciente": self.paciente,
            "cpf": self.cpf,
            "prontuario": self.prontuario,
            "status": status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "faltou_at": self.faltou_at.isoformat() if self.faltou_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }