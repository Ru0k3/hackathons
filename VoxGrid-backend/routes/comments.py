from flask import Blueprint, request, jsonify
from models.comment_model import get_comments_by_discussion, create_comment

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("", methods=["GET"])
@comments_bp.route("/", methods=["GET"])
def fetch_comments():
    discussion_id = request.args.get("discussion_id")

    if not discussion_id:
        return jsonify({"error": "discussion_id is required"}), 400

    comments = get_comments_by_discussion(discussion_id)

    return jsonify(comments)


@comments_bp.route("", methods=["POST"])
@comments_bp.route("/", methods=["POST"])
def add_comment():
    data = request.json

    discussion_id = data.get("discussion_id")
    user_id = data.get("user_id")
    content = data.get("content")

    if not discussion_id or not user_id or not content:
        return jsonify({"error": "Missing required fields"}), 400

    comment_id = create_comment(discussion_id, user_id, content)

    return jsonify({"message": "Comment added", "comment_id": comment_id}), 201
