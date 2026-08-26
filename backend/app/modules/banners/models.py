from sqlalchemy import Boolean, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin

# Same tradeoff as LessonMaterial (see materials/models.py): no object
# storage is configured for this deployment, so the image bytes live
# directly on the row in Postgres. Banners are homepage-facing (result
# showcases, ads, announcements), so keep uploads small — see
# MAX_UPLOAD_BYTES in service.py.


class Banner(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "banners"

    title: Mapped[str] = mapped_column(String(255))
    # Optional destination when a visitor clicks the banner — e.g. a course,
    # an announcement page, or an external link. Empty string means "not
    # clickable," matching the empty-string-default convention used
    # elsewhere (Course.description, Video.title) instead of nullable.
    link_url: Mapped[str] = mapped_column(String(1000), default="")
    image_mime_type: Mapped[str] = mapped_column(String(150))
    image_data: Mapped[bytes] = mapped_column(LargeBinary)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    # Lets an admin temporarily pull a banner from the home page (e.g. a
    # result showcase that's gone stale) without losing/re-uploading it.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
