from datetime import datetime

from src.settings.extensions import db


class MedSpdataAgenda(db.Model):
    __tablename__ = "MED_SPDATA_AGENDA"

    id = db.Column(db.Integer, primary_key=True)

    spdata_agenda_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    id_paciente_spdata = db.Column(db.Integer, nullable=True, index=True)

    crm_atend = db.Column(db.String(50), nullable=True)
    medico = db.Column(db.String(255), nullable=True)

    data_agenda = db.Column(db.Date, nullable=False, index=True)
    hora_agenda = db.Column(db.Time, nullable=True)

    paciente = db.Column(db.String(255), nullable=False, index=True)
    cpf = db.Column(db.String(20), nullable=True, index=True)
    prontuario = db.Column(db.String(50), nullable=True, index=True)

    convenio = db.Column(db.String(100), nullable=True)
    atendido_spdata = db.Column(db.String(1), nullable=True, index=True)

    data_nascimento = db.Column(db.Date, nullable=True)
    celular = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    obs = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __init__(
        self,
        spdata_agenda_id,
        paciente,
        data_agenda,
        id_paciente_spdata=None,
        crm_atend=None,
        medico=None,
        hora_agenda=None,
        cpf=None,
        prontuario=None,
        convenio=None,
        atendido_spdata=None,
        data_nascimento=None,
        celular=None,
        email=None,
        obs=None
    ):
        self.spdata_agenda_id = spdata_agenda_id
        self.id_paciente_spdata = id_paciente_spdata
        self.crm_atend = crm_atend
        self.medico = medico
        self.data_agenda = data_agenda
        self.hora_agenda = hora_agenda
        self.paciente = paciente
        self.cpf = cpf
        self.prontuario = prontuario
        self.convenio = convenio
        self.atendido_spdata = atendido_spdata
        self.data_nascimento = data_nascimento
        self.celular = celular
        self.email = email
        self.obs = obs

    def _to_dict(self):
        return {
            "id": self.id,
            "spdata_agenda_id": self.spdata_agenda_id,
            "id_paciente_spdata": self.id_paciente_spdata,
            "crm_atend": self.crm_atend,
            "medico": self.medico,
            "data_agenda": self.data_agenda.isoformat() if self.data_agenda else None,
            "hora_agenda": str(self.hora_agenda) if self.hora_agenda else None,
            "paciente": self.paciente,
            "cpf": self.cpf,
            "prontuario": self.prontuario,
            "convenio": self.convenio,
            "atendido_spdata": self.atendido_spdata,
            "data_nascimento": self.data_nascimento.isoformat() if self.data_nascimento else None,
            "celular": self.celular,
            "email": self.email,
            "obs": self.obs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
