import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.auth.models import Permission, RefreshToken, Role, RolePermission


def get_role_by_name(db: Session, name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == name))


def get_role_by_id(db: Session, role_id: uuid.UUID) -> Role | None:
    return db.get(Role, role_id)


def get_permission_codes_for_role(db: Session, role_id: uuid.UUID) -> set[str]:
    rows = db.execute(
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    ).all()
    return {row[0] for row in rows}


def create_refresh_token_record(
    db: Session, user_id: uuid.UUID, jti: str, expires_at: datetime
) -> RefreshToken:
    record = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_refresh_token_by_jti(db: Session, jti: str) -> RefreshToken | None:
    return db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))


def revoke_refresh_token(db: Session, record: RefreshToken) -> None:
    record.revoked = True
    db.commit()


def revoke_all_refresh_tokens_for_user(db: Session, user_id: uuid.UUID) -> None:
    """Used on password change so other logged-in sessions are forced to
    re-authenticate with the new password."""
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    db.commit()
