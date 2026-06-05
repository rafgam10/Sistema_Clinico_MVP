from datetime import datetime
from src.settings.extensions import db

""" 
    Armazena medicamentos prescritos.
"""

class Prescricao(db.Model):
    __tablename__ = "prescricoes"

    id = db.Column(db.Integer, primary_key=True)

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False
    )

    medico_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    medicamento = db.Column(
        db.String(255),
        nullable=False
    )

    dosagem = db.Column(
        db.String(100),
        nullable=True
    )

    frequencia = db.Column(
        db.String(100),
        nullable=True
    )

    duracao = db.Column(
        db.String(100),
        nullable=True
    )

    orientacoes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    atendimento = db.relationship(
        "Atendimento",
        back_populates="prescricoes"
    )

    medico = db.relationship(
        "Usuario",
        back_populates="prescricoes"
    )

    def __repr__(self):
        return (
            f"<Prescricao atendimento_id={self.atendimento_id} "
            f"medicamento={self.medicamento}>"
        )