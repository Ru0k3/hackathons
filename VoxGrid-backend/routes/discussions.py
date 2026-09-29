from flask import Blueprint, request, jsonify
from models.discussion_model import (
    get_discussions_by_issue,
    create_discussion,
    get_discussion_by_id,
)

discussions_bp = Blueprint("discussions", __name__)


@discussions_bp.route("", methods=["GET"])
@discussions_bp.route("/", methods=["GET"])
def fetch_discussions():
    issue_id = request.args.get("issue_id")

    if not issue_id:
        return jsonify({"error": "issue_id is required"}), 400

    discussions = get_discussions_by_issue(issue_id)
    print(discussions)
    return jsonify(discussions)


@discussions_bp.route("", methods=["POST"])
@discussions_bp.route("/", methods=["POST"])
def add_discussion():
    data = request.json

    issue_id = data.get("issue_id")
    user_id = data.get("user_id")
    title = data.get("title")
    content = data.get("content")

    if not issue_id or not user_id or not title or not content:
        return jsonify({"error": "Missing required fields"}), 400

    discussion_id = create_discussion(issue_id, user_id, title, content)

    return (
        jsonify({"message": "Discussion created", "discussion_id": discussion_id}),
        201,
    )


@discussions_bp.route("/<int:discussion_id>", methods=["GET"])
def fetch_discussion(discussion_id):
    discussion = get_discussion_by_id(discussion_id)

    if not discussion:
        return jsonify({"error": "Discussion not found"}), 404

    return jsonify(discussion)
