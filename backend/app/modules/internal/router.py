from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.cron import require_cron_secret
from app.modules.users import service as users_service
from app.schemas.envelope import success

router = APIRouter(prefix="/api/v1/internal", tags=["internal"])


@router.post("/send-birthday-emails", dependencies=[Depends(require_cron_secret)])
def send_birthday_emails(db: Annotated[Session, Depends(get_db)]) -> dict:
    sent_count = users_service.send_birthday_emails(db)
    return success({"sent_count": sent_count})
