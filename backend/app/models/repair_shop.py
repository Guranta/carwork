from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin


class RepairShop(Base, IDMixin, TimestampMixin):
    """修理厂/门店（MVP mock）。用于按定位找最近合作门店。"""

    __tablename__ = "repair_shop"

    name: Mapped[str] = mapped_column(String(128), index=True)
    address: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(64), index=True)

    lat: Mapped[float | None] = mapped_column(Numeric(10, 6))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 6))

    labor_rate: Mapped[float | None] = mapped_column(Numeric(10, 2))  # 工时单价(元/小时)
    is_partner: Mapped[bool] = mapped_column(Boolean, default=False)
    brands: Mapped[list] = mapped_column(JSONB, default=list)  # 擅长品牌
    rating: Mapped[float | None] = mapped_column(Numeric(3, 1))
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)
