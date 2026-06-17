from sqlalchemy import Column, String, Integer, DateTime, Time
from datetime import datetime

from src.settings.extensions import db

class MedSpdataAgenda(db.Model):
    
    __tablename__="MED_SPDATA_AGENDA"
    
    id = Column(Integer, primary_key=True)
    medico = Column(String(255), nullable=False)
    data_agenda = Column(DateTime, nullable=False)
    hora_agenda = Column(Time, nullable=False)
    paciente = Column(String(255), nullable=False)
    id_paciente_spdata = Column(Integer, nullable=False)
    cpf = Column(String(20), nullable=False)
    prontuario = Column(Integer, nullable=False)
    atendido_spdata = Column(String(50), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    
    def __init__(self, medico, data_agenda, hora_agenda, paciente, id_paciente_spdata, cpf, prontuario, atendido_spdata):
        self.medico = medico
        self.data_agenda = data_agenda
        self.hora_agenda = hora_agenda
        self.paciente = paciente
        self.id_paciente_spdata = id_paciente_spdata
        self.cpf = cpf
        self.prontuario = prontuario
        self.atendido_spdata = atendido_spdata
        
        
    def _to_dict(self):
        return {
            "médico": self.medico,
            "data_agenda": self.data_agenda,
            "hora_agenda": self.hora_agenda,
            "paciente": self.paciente,
            "id_paciente_spdata": self.id_paciente_spdata,
            "cpf": self.cpf,
            "prontuario": self.prontuario,
            "atendido_spdata": self.atendido_spdata
        }