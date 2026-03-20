from functools import wraps

from flask import redirect, session, url_for

from bari_lms.config import ROLE_TO_SLUG
from bari_lms.models.repository import get_user_by_email


def current_user():
    email = session.get("user_email")
    if not email:
        return None

    user = get_user_by_email(email)
    if user is None or not user["active"]:
        session.clear()
        return None

    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "name": user["name"],
        "active": user["active"],
        "dashboard_slug": ROLE_TO_SLUG[user["role"]],
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def role_required(expected_role):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            user = current_user()
            if user is None:
                return redirect(url_for("login"))
            if user["role"] != expected_role:
                return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))
            return view(**kwargs)

        return wrapped_view

    return decorator


def session_context():
    return {
        "session_user": current_user(),
        "session_user_email": session.get("user_email", ""),
    }
