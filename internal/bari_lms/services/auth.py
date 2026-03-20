# Re-exportaciones para compatibilidad — la lógica vive en middleware.auth
from bari_lms.middleware.auth import (  # noqa: F401
    current_user,
    login_required,
    role_required,
    session_context,
)
