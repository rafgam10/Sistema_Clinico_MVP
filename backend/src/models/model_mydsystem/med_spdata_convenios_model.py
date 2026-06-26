from datetime import datetime

from src.settings.extensions import db


class MedSpdataConvenio(db.Model):
    __tablename__ = "MED_SPDATA_CONVENIOS"

    id = db.Column(db.Integer, primary_key=True)
    codigo_spdata = db.Column(db.Integer, nullable=False, unique=True, index=True)
    nome = db.Column(db.String(255), nullable=False, index=True)
    situacao = db.Column(db.String(50), nullable=True, index=True)
    registro_ans = db.Column(db.String(50), nullable=True)
    dados_spdata = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def _to_dict(self):
        return {
            "id": self.id,
            "codigo_spdata": self.codigo_spdata,
            "nome": self.nome,
            "situacao": self.situacao,
            "registro_ans": self.registro_ans,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
