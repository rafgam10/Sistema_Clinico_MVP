from datetime import datetime

from src.settings.extensions import db


class ModeloOrientacaoExame(db.Model):
    __tablename__ = "MODELO_ORIENTACAO_EXAME"

    id = db.Column(db.Integer, primary_key=True)
    nome_modelo = db.Column(db.String(255), nullable=False)
    medico_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    conteudo = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __init__(self, nome_modelo, medico_id, conteudo):
        self.nome_modelo = nome_modelo
        self.medico_id = medico_id
        self.conteudo = conteudo

    def __repr__(self):
        return f"<ModeloOrientacaoExame id={self.id} nome_modelo={self.nome_modelo}>"

    def _to_dict(self):
        return {
            "id": self.id,
            "nome_modelo": self.nome_modelo,
            "medico_id": self.medico_id,
            "conteudo": self.conteudo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
