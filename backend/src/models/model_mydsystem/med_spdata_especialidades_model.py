from datetime import datetime

from src.settings.extensions import db


class MedSpdataEspecialidade(db.Model):
    __tablename__ = "MED_SPDATA_ESPECIALIDADES"

    id = db.Column(db.Integer, primary_key=True)
    codigo_spdata = db.Column(db.Integer, nullable=False, unique=True, index=True)
    nome = db.Column(db.String(255), nullable=False, index=True)
    cred = db.Column(db.String(50), nullable=True, index=True)
    refexp = db.Column(db.String(50), nullable=True)
    sigla = db.Column(db.String(50), nullable=True, index=True)
    idade_inicial = db.Column(db.Integer, nullable=True)
    idade_final = db.Column(db.Integer, nullable=True)
    sexo = db.Column(db.String(20), nullable=True, index=True)
    id_tbdigital_especialidade = db.Column(db.Integer, nullable=True)
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
            "cred": self.cred,
            "refexp": self.refexp,
            "sigla": self.sigla,
            "idade_inicial": self.idade_inicial,
            "idade_final": self.idade_final,
            "sexo": self.sexo,
            "id_tbdigital_especialidade": self.id_tbdigital_especialidade,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
