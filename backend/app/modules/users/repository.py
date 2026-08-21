import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.models import ParentProfile, StudentProfile, TeacherProfile, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def list_users(db: Session, offset: int, limit: int) -> tuple[list[User], int]:
    items = db.scalars(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    ).all()
    total = db.scalar(select(func.count()).select_from(User)) or 0
    return list(items), total


def create_user(db: Session, *, email: str, password_hash: str, full_name: str, phone: str | None,
                 role_id: uuid.UUID) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        phone=phone,
        role_id=role_id,
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
