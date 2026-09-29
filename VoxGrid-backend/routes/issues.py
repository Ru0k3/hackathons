from flask import Blueprint, request, jsonify
from models.issue_model import create_issue, get_all_issues, get_issue_by_id

issues_bp = Blueprint("issues", __name__)


# ----------------------
# Create a new issue
# ----------------------
@issues_bp.route("/", methods=["POST"])
def add_issue():
    data = request.get_json()

    title = data.get("title")
    summary = data.get("summary")
    category_id = data.get("category_id")

    # basic validation
    if not title or not summary or not category_id:
        return jsonify({"error": "Missing required fields"}), 400

    issue_id = create_issue(title, summary, category_id)

    return jsonify({"message": "Issue created successfully", "issue_id": issue_id}), 201


# ----------------------
# Fetch issues (optionally by category)
# ----------------------
@issues_bp.route("", methods=["GET"])
@issues_bp.route("/", methods=["GET"])
def fetch_issues():
    # Get category_id as integer from query string
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort")  # optional: "latest"

    issues = get_all_issues(category_id=category_id, sort=sort)

    # Return as a flat array
    return jsonify(issues)


# ----------------------
# Fetch a single issue by ID
# ----------------------
@issues_bp.route("/<int:issue_id>", methods=["GET"])
def fetch_issue(issue_id):
    issue = get_issue_by_id(issue_id)

    if not issue:
        return jsonify({"error": "Issue not found"}), 404

    return jsonify(issue)
