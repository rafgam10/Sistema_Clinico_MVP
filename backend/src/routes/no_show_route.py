from flask import Blueprint, request, jsonify

NoShow_bp = Blueprint("no_show", __name__, url_prefix="no_show")


@NoShow_bp.route("/", methods=["GET"])
def index():
    ...