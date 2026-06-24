from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    id_card: Mapped[str | None] = mapped_column(String(64))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="user")
    avatar: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    org_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("organization.id"))


class Staff(Base, IDMixin, TimestampMixin):
    __tablename__ = "staff"

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    employee_no: Mapped[str | None] = mapped_column(String(64))
    position: Mapped[str | None] = mapped_column(String(64))
    org_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("organization.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
