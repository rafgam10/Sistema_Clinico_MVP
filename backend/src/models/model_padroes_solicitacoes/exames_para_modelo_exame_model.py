from datetime import datetime
from src.settings.extensions import db


class ExamesDoModelo(db.Model):
    __tablename__ = "EXAMES_MODELO_EXAME"

    id = db.Column(db.Integer, primary_key=True)
    nome_exame = db.Column(db.String(255), nullable=False)
    exame_id = db.Column(
        db.Integer,
        db.ForeignKey("exames.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    id_modelo_solicitacao_exame = db.Column(
        db.Integer,
        db.ForeignKey("MODELO_SOLICITACAO_EXAME.id"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    modelo_solicitacao_exame = db.relationship(
        "ModeloExame", back_populates="exames"
    )

    exame = db.relationship(
        "Exame", back_populates="exames_modelo"
    )

    def __init__(self, nome_exame, id_modelo_solicitacao_exame, exame_id=None):
        self.nome_exame = nome_exame
        self.id_modelo_solicitacao_exame = id_modelo_solicitacao_exame
        self.exame_id = exame_id

    def __repr__(self):
        return f"<ExamesDoModelo id={self.id} nome_exame={self.nome_exame}>"

    def _to_dict(self):
        return {
            "id": self.id,
            "nome_exame": self.nome_exame,
            "exame_id": self.exame_id,
            "exame": {
                "id": self.exame.id,
                "nome": self.exame.nome,
                "codigo_alfanumerico": self.exame.codigo_alfanumerico,
                "codigo_amb": self.exame.codigo_amb,
            } if self.exame else None,
            "id_modelo_solicitacao_exame": self.id_modelo_solicitacao_exame,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
