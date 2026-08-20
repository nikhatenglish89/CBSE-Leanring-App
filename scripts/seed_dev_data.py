"""Local dev seed: default roles/permissions + 5 demo accounts (one per role
family used at this phase). DEV ONLY — these are not real secrets and must
never be reused for a real deployment.

Run from `backend/` with the project venv active:
    python ../scripts/seed_dev_data.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.append(str(BACKEND_DIR))

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.modules.auth import models as auth_models  # noqa: E402,F401
from app.modules.auth.seed import seed_roles_and_permissions  # noqa: E402
from app.modules.users import models as users_models  # noqa: E402,F401
from app.modules.users import repository as users_repo  # noqa: E402

DEV_PASSWORD = "DevPass123!"  # DEV ONLY

DEMO_USERS = [
    ("admin@edusphere.dev", "Demo Admin", "ADMIN"),
    ("teacher@edusphere.dev", "Demo Teacher", "TEACHER"),
    ("student@edusphere.dev", "Demo Student", "STUDENT"),
    ("parent@edusphere.dev", "Demo Parent", "PARENT"),
    ("support@edusphere.dev", "Demo Support Agent", "SUPPORT_AGENT"),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        roles = seed_roles_and_permissions(db)

        for email, full_name, role_name in DEMO_USERS:
            if users_repo.get_user_by_email(db, email) is not None:
                print(f"skip (exists): {email}")
                continue
            role = roles[role_name]
            user = users_repo.create_user(
                db,
                email=email,
                password_hash=hash_password(DEV_PASSWORD),
                full_name=full_name,
                phone=None,
                role_id=role.id,
            )
            if role_name == "STUDENT":
                users_repo.create_student_profile(db, user.id)
            elif role_name == "PARENT":
                users_repo.create_parent_profile(db, user.id)
            elif role_name == "TEACHER":
                users_repo.create_teacher_profile(db, user.id)
            print(f"created: {email} / {DEV_PASSWORD} (role={role_name})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
