# backend/app/user_profiles.py

from typing import Dict, Optional

"""
This file handles user preference storage for Negotiator AI.
It is used by:
- Preferences API
- Matching Engine
- Watsonx Orchestrate (decision-making)

Hackathon choice:
- In-memory storage (fast, simple, explainable to judges)
"""

# -----------------------------
# In-memory database
# Key   -> Slack User ID
# Value -> User preference dictionary
# -----------------------------

USER_PROFILES: Dict[str, dict] = {}


# -----------------------------
# Save or update user profile
# -----------------------------
def save_user_profile(slack_id: str, preferences: dict) -> None:
    """
    Save or update a user's meeting preferences.

    Example preferences:
    {
        "preferred_time": "Evening",
        "duration": "30 mins",
        "flexibility": "Flexible",
        "avoid_days": ["Monday", "Friday"]
    }
    """
    USER_PROFILES[slack_id] = preferences


# -----------------------------
# Fetch a user profile
# -----------------------------
def get_user_profile(slack_id: str) -> Optional[dict]:
    """
    Retrieve user preferences for AI negotiation.
    Returns None if user does not exist.
    """
    return USER_PROFILES.get(slack_id)


# -----------------------------
# Fetch all profiles (debug / demo)
# -----------------------------
def get_all_user_profiles() -> Dict[str, dict]:
    """
    Returns all stored user profiles.
    Useful for debugging or hackathon demos.
    """
    return USER_PROFILES


# -----------------------------
# Delete a user profile (optional)
# -----------------------------
def delete_user_profile(slack_id: str) -> None:
    """
    Remove a user's preferences.
    Called on logout if needed.
    """
    if slack_id in USER_PROFILES:
        del USER_PROFILES[slack_id]
