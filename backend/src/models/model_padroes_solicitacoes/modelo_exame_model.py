from datetime import datetime
from src.settings.extensions import db


class ModeloExame(db.Model):
    __tablename__ = "MODELO_SOLICITACAO_EXAME"

    id = db.Column(db.Integer, primary_key=True)
    nome_modelo = db.Column(db.String(255), nullable=False)
    medico_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    exames = db.relationship(
        "ExamesDoModelo",
        back_populates="modelo_solicitacao_exame",
        cascade="all, delete-orphan",
        order_by="ExamesDoModelo.created_at.desc()",
    )

    def __init__(self, nome_modelo, medico_id):
        self.nome_modelo = nome_modelo
        self.medico_id = medico_id

    def __repr__(self):
        return f"<ModeloExame id={self.id} nome_modelo={self.nome_modelo}>"

    def _to_dict(self):
        return {
            "id": self.id,
            "nome_modelo": self.nome_modelo,
            "medico_id": self.medico_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
