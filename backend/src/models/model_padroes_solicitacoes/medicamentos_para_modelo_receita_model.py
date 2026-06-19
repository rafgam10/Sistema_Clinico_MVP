from datetime import datetime

from src.settings.extensions import db


class Medicamentos(db.Model):
    __tablename__ = "MEDICAMENTOS_MODELO_RECEITA"

    id = db.Column(db.Integer, primary_key=True)

    nome_medicamento = db.Column(
        db.String(255),
        nullable=False
    )

    dosagem = db.Column(
        db.String(15),
        nullable=False
    )

    detalhes = db.Column(
        db.Text,
        nullable=True
    )

    id_modelo_solicitacao_receita = db.Column(
        db.Integer,
        db.ForeignKey("MODELO_SOLICITACAO_RECEITA.id"),
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

    modelo_solicitacao_receita = db.relationship(
        "ModeloReceita",
        back_populates="medicamentos"
    )


    def __init__(self, nome_medicamento, dosagem, detalhes, id_modelo_solicitacao_receita):
        self.nome_medicamento = nome_medicamento
        self.dosagem = dosagem
        self.detalhes = detalhes
        self.id_modelo_solicitacao_receita = id_modelo_solicitacao_receita

    def __repr__(self):
        return (
            f"<Medicamentos id={self.id} "
            f"nome_medicamento={self.nome_medicamento}>"
        )
        
    def _to_dict(self):
        return {
            "id": self.id,
            "nome_medicamento": self.nome_medicamento,
            "dosagem": self.dosagem,
            "detalhes": self.detalhes,
            "id_modelo_solicitacao_receita": self.id_modelo_solicitacao_receita,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }