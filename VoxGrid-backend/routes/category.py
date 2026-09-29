from flask import Blueprint, jsonify
from models.category_model import fetch_categories

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/", methods=["GET"])
def get_categories():
    categories = fetch_categories()
    return jsonify(categories)
