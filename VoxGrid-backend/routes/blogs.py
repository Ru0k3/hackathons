from flask import Blueprint, request, jsonify

from models.blog_model import fetch_blogs, fetch_blog_by_id, add_blog

blogs_bp = Blueprint("blogs", __name__)


@blogs_bp.route("", methods=["GET"])
@blogs_bp.route("/", methods=["GET"])
def get_blogs():

    issue_id = request.args.get("issue_id")

    blogs = fetch_blogs(issue_id)

    return jsonify(blogs)


@blogs_bp.route("/<int:blog_id>", methods=["GET"])
def get_blog(blog_id):

    blog = fetch_blog_by_id(blog_id)

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    return jsonify(blog)


@blogs_bp.route("", methods=["POST"])
@blogs_bp.route("/", methods=["POST"])
def create_blog():

    data = request.get_json()

    issue_id = data.get("issue_id")
    user_id = data.get("user_id")
    title = data.get("title")
    content = data.get("content")

    if not all([issue_id, user_id, title, content]):
        return jsonify({"error": "Missing required fields"}), 400

    blog_id = add_blog(issue_id, user_id, title, content)

    return jsonify({"message": "Blog created successfully", "blog_id": blog_id}), 201
