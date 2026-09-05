import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.modules.auth.models import Role
from app.modules.users.models import ParentProfile, StudentProfile, TeacherProfile, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def list_users(
    db: Session, offset: int, limit: int, *, role: str | None = None, search: str | None = None
) -> tuple[list[User], int]:
    stmt = select(User)
    if role is not None:
        stmt = stmt.join(Role, User.role_id == Role.id).where(Role.name == role)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)).all()
    return list(items), total


def create_user(db: Session, *, email: str, password_hash: str, full_name: str, phone: str | None,
                 role_id: uuid.UUID, password_reset_required: bool = False) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        phone=phone,
        role_id=role_id,
        password_reset_required=password_reset_required,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_student_profile(db: Session, user_id: uuid.UUID) -> StudentProfile:
    profile = StudentProfile(user_id=user_id)
    db.add(profile)
    db.commit()
    return profile


def create_parent_profile(db: Session, user_id: uuid.UUID) -> ParentProfile:
    profile = ParentProfile(user_id=user_id)
    db.add(profile)
    db.commit()
    return profile


def create_teacher_profile(db: Session, user_id: uuid.UUID) -> TeacherProfile:
    profile = TeacherProfile(user_id=user_id)
    db.add(profile)
    db.commit()
    return profile


def get_teacher_profile_by_user_id(db: Session, user_id: uuid.UUID) -> TeacherProfile | None:
    return db.scalar(select(TeacherProfile).where(TeacherProfile.user_id == user_id))


def get_teacher_profile_by_id(db: Session, profile_id: uuid.UUID) -> TeacherProfile | None:
    return db.get(TeacherProfile, profile_id)


def get_student_profile_by_user_id(db: Session, user_id: uuid.UUID) -> StudentProfile | None:
    return db.scalar(select(StudentProfile).where(StudentProfile.user_id == user_id))


def get_parent_profile_by_user_id(db: Session, user_id: uuid.UUID) -> ParentProfile | None:
    return db.scalar(select(ParentProfile).where(ParentProfile.user_id == user_id))


def get_parent_profile_by_id(db: Session, profile_id: uuid.UUID) -> ParentProfile | None:
    return db.get(ParentProfile, profile_id)


def list_students_for_parent_profile(db: Session, parent_profile_id: uuid.UUID) -> list[StudentProfile]:
    stmt = select(StudentProfile).where(StudentProfile.parent_profile_id == parent_profile_id)
    return list(db.scalars(stmt))


def set_student_parent(
    db: Session, profile: StudentProfile, parent_profile_id: uuid.UUID | None
) -> StudentProfile:
    profile.parent_profile_id = parent_profile_id
    db.commit()
    db.refresh(profile)
    return profile


def set_teacher_verified(db: Session, profile: TeacherProfile, verified: bool) -> TeacherProfile:
    profile.verified = verified
    db.commit()
    db.refresh(profile)
    return profile


def set_student_verified(db: Session, profile: StudentProfile, verified: bool) -> StudentProfile:
    profile.verified = verified
    db.commit()
    db.refresh(profile)
    return profile


def clear_password_reset_required(db: Session, user: User) -> User:
    user.password_reset_required = False
    db.commit()
    db.refresh(user)
    return user


def mark_email_verified(db: Session, user: User) -> User:
    user.email_verified_at = utcnow()
    db.commit()
    db.refresh(user)
    return user
