from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class ClaimCase(Base, IDMixin, TimestampMixin):
    __tablename__ = "claim_case"

    case_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    insurance_policy_no: Mapped[str | None] = mapped_column(String(64), index=True)
    insurance_company: Mapped[str | None] = mapped_column(String(128))
    vehicle_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("vehicle.id"))
    claimant_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
    handler_staff_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("staff.id"))
    org_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("organization.id"))

    incident_at: Mapped[str | None] = mapped_column(String(32))
    incident_location: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(16), default="reported", index=True)
    stage: Mapped[str | None] = mapped_column(String(16))

    loss_assessment: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    estimated_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    settled_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    risk_flags: Mapped[list | None] = mapped_column(JSONB, default=list)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)


class ServiceOrder(Base, IDMixin, TimestampMixin):
    __tablename__ = "service_order"

    order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    vehicle_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("vehicle.id"))
    org_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("organization.id"))
    advisor_staff_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("staff.id"))
    technician_staff_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("staff.id"))

    fault_desc: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="created", index=True)
    items: Mapped[list | None] = mapped_column(JSONB, default=list)
    total_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    claim_case_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("claim_case.id"))
