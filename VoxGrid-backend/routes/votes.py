from flask import Blueprint, request, jsonify
from models.vote_model import add_vote, get_vote_counts

votes_bp = Blueprint("votes", __name__)


# For discussions and comments
@votes_bp.route("", methods=["POST"])
@votes_bp.route("/", methods=["POST"])
def vote():
    data = request.json

    target_type = data.get("target_type")  # discussion | comment
    target_id = data.get("target_id")
    vote_type = data.get("vote_type")  # agree | disagree

    if target_type not in ["discussion", "comment"]:
        return jsonify({"error": "Invalid target_type"}), 400

    if vote_type not in ["agree", "disagree"]:
        return jsonify({"error": "Invalid vote_type"}), 400

    add_vote(target_type, target_id, vote_type)

    counts = get_vote_counts(target_type, target_id)

    return jsonify({"message": "Vote recorded", "counts": counts})
