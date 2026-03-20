# Re-exportaciones para compatibilidad con código existente.
# La lógica vive en los módulos db/ y repositories/.

from bari_lms.db import (  # noqa: F401
    close_db,
    create_pool,
    get_db,
    parse_int,
    parse_uuid,
)
from bari_lms.db.bootstrap import initialize_database  # noqa: F401
from bari_lms.repositories import (  # noqa: F401
    ACADEMIC_ENTITIES,
    ENTITY_CONFIG,
    PEOPLE_ENTITIES,
    STRUCTURE_ENTITIES,
    academic_redirect_args,
    create_linked_person_user,
    delete_entity,
    delete_linked_person_user,
    entity_form_data,
    get_admin_dashboard_data,
    get_all_users,
    get_entities,
    get_entity,
    get_people_redirect_args,
    get_user_by_email,
    get_user_by_id,
    insert_entity,
    normalize_academic_context,
    normalize_people_context,
    normalize_structure_context,
    structure_redirect_args,
    sync_linked_person_user,
    update_entity,
    user_has_profile,
    validate_academic_payload,
    validate_entity_payload,
)
