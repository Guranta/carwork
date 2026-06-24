from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class Vehicle(Base, IDMixin, TimestampMixin):
    __tablename__ = "vehicle"

    vin: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    plate_no: Mapped[str | None] = mapped_column(String(16), index=True)
    brand: Mapped[str | None] = mapped_column(String(64))
    model: Mapped[str | None] = mapped_column(String(128))
    year: Mapped[int | None] = mapped_column()
    color: Mapped[str | None] = mapped_column(String(32))
    engine_no: Mapped[str | None] = mapped_column(String(64))
    attrs: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    owner_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))


class MaintenanceRecord(Base, IDMixin, TimestampMixin):
    __tablename__ = "maintenance_record"

    vehicle_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vehicle.id"), index=True)
    org_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("organization.id"))
    service_date: Mapped[str | None] = mapped_column(String(32))
    mileage: Mapped[int | None] = mapped_column()
    items: Mapped[list | None] = mapped_column(JSONB, default=list)
    summary: Mapped[str | None] = mapped_column(String(512))
