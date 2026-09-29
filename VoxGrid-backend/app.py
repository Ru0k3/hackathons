from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from routes import issues, users, comments, discussions, votes, polls, category, blogs

app = Flask(__name__)
CORS(app)

app.register_blueprint(users.auth_bp, url_prefix="/auth")
app.register_blueprint(issues.issues_bp, url_prefix="/issues")
app.register_blueprint(comments.comments_bp, url_prefix="/comments")
app.register_blueprint(discussions.discussions_bp, url_prefix="/discussions")
app.register_blueprint(category.categories_bp, url_prefix="/categories")
app.register_blueprint(votes.votes_bp, url_prefix="/votes")
app.register_blueprint(polls.polls_bp, url_prefix="/polls")
app.register_blueprint(blogs.blogs_bp, url_prefix="/blogs")

if __name__ == "__main__":
    app.run(debug=True)
