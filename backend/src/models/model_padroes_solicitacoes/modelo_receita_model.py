from datetime import datetime

from src.settings.extensions import db


class ModeloReceita(db.Model):
    __tablename__ = "MODELO_SOLICITACAO_RECEITA"

    id = db.Column(db.Integer, primary_key=True)

    nome_modelo = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    medicamentos = db.relationship(
        "Medicamentos",
        back_populates="modelo_solicitacao_receita",
        cascade="all, delete-orphan",
        order_by="Medicamentos.created_at.desc()"
    )
    
    def __init__(self, nome_modelo):
        self.nome_modelo = nome_modelo

    def __repr__(self):
        return f"<ModeloReceita id={self.id} nome_modelo={self.nome_modelo}>"
    
    def _to_dict(self):
        return {
            "id": self.id,
            "nome_modelo": self.nome_modelo,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
