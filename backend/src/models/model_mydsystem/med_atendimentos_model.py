from sqlalchemy import Column, String, Integer, DateTime, Time
from sqlalchemy import Enum as SQLEnum
from datetime import datetime

from enum import Enum

from src.settings.extensions import db


class Status_Atendimento(Enum):
    EM_ATENDIMENTO = 'em_atendimento'
    ATENDIDO = 'atendido'
    FALTOU = 'faltou'

class MedAtendimentos(db.Model):
    
    __tablename__="MED_ATENDIMENTOS"
    
    id = Column(Integer, primary_key=True)
    id_medico_spdata = Column(Integer, nullable=False)
    medico = Column(String(255), nullable=False)
    data_agenda = Column(DateTime, nullable=False)
    hora_agenda = Column(Time, nullable=False)
    id_paciente_spdata = Column(Integer, nullable=False)
    paciente = Column(String(255), nullable=False)
    cpf = Column(String(20), nullable=False)
    prontuario = Column(Integer, nullable=False)
    
    status = Column(SQLEnum(Status_Atendimento), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=False)
    faltou_at = Column(DateTime, nullable=True)
    
    def __init__(self, id_medico_spdata, medico, data_agenda, hora_agenda, id_paciente_spdata, paciente, cpf, prontuario, status, started_at, finished_at, faltou_at=None):
        self.id_medico_spdata = id_medico_spdata
        self.medico = medico
        self.data_agenda = data_agenda
        self.hora_agenda = hora_agenda
        self.id_paciente_spdata = id_paciente_spdata
        self.paciente = paciente
        self.cpf = cpf
        self.prontuario = prontuario
        self.status = status
        self.started_at = started_at
        self.finished_at = finished_at
        self.faltou_at = faltou_at
        
    def _to_dict(self):
        return {
            "id_medico_spdata": self.id_medico_spdata,
            "medico": self.medico,
            "data_agenda": self.data_agenda,
            "hora_agenda": self.hora_agenda,
            "id_paciente_spdata": self.id_paciente_spdata,
            "paciente": self.paciente,
            "cpf": self.cpf,
            "prontuario": self.prontuario,
            "status": self.status.value if hasattr(self.status, "value") else self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "faltou_at": self.faltou_at
        }
