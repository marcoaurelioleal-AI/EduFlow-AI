ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_VIEWER = "viewer"

USER_ROLES = {ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER}

ROLE_LEVELS = {
    ROLE_VIEWER: 1,
    ROLE_OPERATOR: 2,
    ROLE_ADMIN: 3,
}


def has_role_level(user_role: str, minimum_role: str) -> bool:
    return ROLE_LEVELS.get(user_role, 0) >= ROLE_LEVELS[minimum_role]
