from flask import Blueprint, request, jsonify

spdata_bp = Blueprint("spdata", __name__, url_prefix="/spdata")

@spdata_bp.route("/")
def spdata_paciente():
    ...