from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime

from src.settings.extensions import db

class Medico(db.Model):
    __tablename__ = "medicos"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        unique=True,
        index=True
    )

    spdata_id = db.Column(db.Integer, nullable=True, unique=True, index=True)

    crm = db.Column(db.String(20), nullable=False)
    crm_uf = db.Column(db.String(2), nullable=False)
    rqe = db.Column(db.String(30), nullable=True)
    especialidade = db.Column(db.String(120), nullable=True)

    ativo = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="medico"
    )
    
    def __init__(self, usuario_id, spdate_id, crm, crm_uf, rqe, especialidade, ativo):
        self.usuario_id = usuario_id
        self.spdata_id = self.spdata_id
        self.crm = crm
        self.crm_uf = crm_uf
        self.rqe = rqe
        self.especialidade = especialidade
        self.ativo = ativo
        
    def _to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "spdata_id": self.spdata_id,
            "crm": self.crm,
            "crm_uf": self.crm_uf,
            "especialidade": self.especialidade,
            "ativo": self.ativo,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }