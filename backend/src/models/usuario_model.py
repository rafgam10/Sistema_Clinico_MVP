from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime

from src.settings.extensions import db

class Usuario(db.Model):
    
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relações
    evolucoes_medicas = db.relationship(
        "EvolucaoMedica",
        back_populates="medico"
    )


    alteracoes_evolucoes = db.relationship(
        "EvolucaoMedicaVersao",
        back_populates="usuario_alteracao"
    )

    prescricoes = db.relationship(
        "Prescricao",
        back_populates="medico"
    )

    auditorias = db.relationship(
        "Auditoria",
        foreign_keys="Auditoria.usuario_id",
        back_populates="usuario"
    )

    auditorias_medicas = db.relationship(
        "Auditoria",
        foreign_keys="Auditoria.medico_id",
        back_populates="medico"
    )
    
    def __init__(self, email, senha):
        self.email = email
        self.senha = senha


    def __repr__(self):
        return f"Usuario: {self.email} - {self.senha}"
    
    def _to_dict_(self):
        return {
            "id": self.id,
            "email": self.email,
            "senha": self.senha
        }