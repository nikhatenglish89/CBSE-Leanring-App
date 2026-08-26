import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.banners.models import Banner


def list_active_banners(db: Session) -> list[Banner]:
    stmt = (
        select(Banner)
        .where(Banner.is_active.is_(True))
        .order_by(Banner.display_order, Banner.created_at)
    )
    return list(db.scalars(stmt))


def list_all_banners(db: Session) -> list[Banner]:
    stmt = select(Banner).order_by(Banner.display_order, Banner.created_at)
    return list(db.scalars(stmt))


def get_banner_by_id(db: Session, banner_id: uuid.UUID) -> Banner | None:
    return db.get(Banner, banner_id)


def create_banner(db: Session, **fields) -> Banner:
    obj = Banner(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_banner(
    db: Session,
    obj: Banner,
    *,
    title: str | None,
    link_url: str | None,
    display_order: int | None,
    is_active: bool | None,
) -> Banner:
    if title is not None:
        obj.title = title
    if link_url is not None:
        obj.link_url = link_url
    if display_order is not None:
        obj.display_order = display_order
    if is_active is not None:
        obj.is_active = is_active
    db.commit()
    db.refresh(obj)
    return obj


def delete_banner(db: Session, obj: Banner) -> None:
    db.delete(obj)
    db.commit()
