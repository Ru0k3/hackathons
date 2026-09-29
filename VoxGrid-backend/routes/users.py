from flask import Blueprint, request, jsonify
from models.user_model import login_user, add_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    result = add_user(name, email, password)

    if result["success"]:
        return jsonify({"message": "User created"})
    else:
        return jsonify({"error": result["error"]}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = login_user(email, password)

    if user:
        return jsonify(
            {
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                },
            }
        )
    else:
        return jsonify({"message": "Invalid credentials"}), 401
