from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.cron import require_cron_secret
from app.modules.users import service as users_service
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/internal", tags=["internal"])


# TEMPORARY — diagnosing why CRON_SECRET set in Render isn't taking effect.
# Reveals presence/length only, never the value. Remove once resolved.
@router.get("/debug-config-check")
def debug_config_check() -> dict:
    return success(
        {
            "cron_secret_set": bool(settings.CRON_SECRET),
            "cron_secret_length": len(settings.CRON_SECRET),
            "resend_api_key_set": bool(settings.RESEND_API_KEY),
            "resend_from_email": settings.RESEND_FROM_EMAIL,
        }
    )


@router.post("/send-birthday-emails", dependencies=[Depends(require_cron_secret)])
def send_birthday_emails(db: Annotated[Session, Depends(get_db)]) -> dict:
    sent_count = users_service.send_birthday_emails(db)
    return success({"sent_count": sent_count})
