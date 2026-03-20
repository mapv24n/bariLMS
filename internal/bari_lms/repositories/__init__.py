"""Re-exportaciones del paquete repositories para compatibilidad con código existente."""

from bari_lms.repositories._config import (
    ACADEMIC_ENTITIES,
    ENTITY_CONFIG,
    PEOPLE_ENTITIES,
    PERSON_USER_CONFIG,
    STRUCTURE_ENTITIES,
)
from bari_lms.repositories.admin.academico import academic_redirect_args, normalize_academic_context
from bari_lms.repositories.entidad import (
    delete_entity,
    entity_form_data,
    get_entities,
    get_entity,
    insert_entity,
    update_entity,
    validate_academic_payload,
    validate_entity_payload,
)
from bari_lms.repositories.admin.estructura import normalize_structure_context, structure_redirect_args
from bari_lms.repositories.admin.personas import (
    create_linked_person_user,
    delete_linked_person_user,
    get_people_redirect_args,
    normalize_people_context,
    sync_linked_person_user,
)
from bari_lms.repositories.usuario import (
    get_admin_dashboard_data,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    user_has_profile,
)

__all__ = [
    "ACADEMIC_ENTITIES",
    "ENTITY_CONFIG",
    "PEOPLE_ENTITIES",
    "PERSON_USER_CONFIG",
    "STRUCTURE_ENTITIES",
    "academic_redirect_args",
    "normalize_academic_context",
    "delete_entity",
    "entity_form_data",
    "get_entities",
    "get_entity",
    "insert_entity",
    "update_entity",
    "validate_academic_payload",
    "validate_entity_payload",
    "normalize_structure_context",
    "structure_redirect_args",
    "create_linked_person_user",
    "delete_linked_person_user",
    "get_people_redirect_args",
    "normalize_people_context",
    "sync_linked_person_user",
    "get_admin_dashboard_data",
    "get_all_users",
    "get_user_by_email",
    "get_user_by_id",
    "user_has_profile",
]
