"""Canonical role/permission catalog — the single source of truth used by both
the dev seed script (scripts/seed_dev_data.py) and the test suite, so the two
never drift apart.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import Permission, Role, RolePermission

# Baseline permission catalog (master spec §22 examples, kept intentionally
# small for Phase 2 — grows as later phases add resources).
DEFAULT_PERMISSIONS: list[tuple[str, str]] = [
    ("user:view", "View other users' accounts"),
    ("user:update", "Update other users' accounts"),
    ("user:delete", "Delete/deactivate user accounts"),
    ("course:create", "Create courses"),
    ("course:update", "Update courses"),
    ("course:delete", "Delete courses"),
    ("course:view", "View courses"),
    ("test:create", "Create tests"),
    ("test:update", "Update tests"),
    ("test:publish", "Publish tests"),
    ("payment:view", "View payment records"),
    ("payment:refund", "Issue refunds"),
]

ALL_CODES = [code for code, _ in DEFAULT_PERMISSIONS]

DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "SUPER_ADMIN": ALL_CODES,
    "ADMIN": ALL_CODES,
    "CONTENT_MANAGER": ["course:create", "course:update", "course:delete", "course:view",
                          "test:create", "test:update", "test:publish"],
    "TEACHER": ["course:view", "test:create", "test:update"],
    "SUPPORT_AGENT": ["user:view", "payment:view"],
    "STUDENT": ["course:view"],
    "PARENT": ["course:view"],
}

DEFAULT_ROLES = list(DEFAULT_ROLE_PERMISSIONS.keys())


def seed_roles_and_permissions(db: Session) -> dict[str, Role]:
    """Idempotent: safe to call every app/test startup."""
    roles_by_name: dict[str, Role] = {}
    for name in DEFAULT_ROLES:
        role = db.scalar(select(Role).where(Role.name == name))
        if role is None:
            role = Role(name=name)
            db.add(role)
            db.flush()
        roles_by_name[name] = role

    permissions_by_code: dict[str, Permission] = {}
    for code, description in DEFAULT_PERMISSIONS:
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, description=description)
            db.add(permission)
            db.flush()
        permissions_by_code[code] = permission

    for role_name, codes in DEFAULT_ROLE_PERMISSIONS.items():
        role = roles_by_name[role_name]
        for code in codes:
            permission = permissions_by_code[code]
            exists = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )
            if exists is None:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    db.commit()
    return roles_by_name
