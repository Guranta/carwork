from sqlalchemy import BigInteger, Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin


class Policy(Base, IDMixin, TimestampMixin):
    """保单（MVP mock）。用于查询险种、免赔额、赔付比例，支撑"报销价"理算。"""

    __tablename__ = "policy"

    policy_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    insured_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
    insured_name: Mapped[str | None] = mapped_column(String(64))
    insured_phone: Mapped[str | None] = mapped_column(String(32))

    plate_no: Mapped[str | None] = mapped_column(String(16), index=True)
    vin: Mapped[str | None] = mapped_column(String(32), index=True)

    insurance_company: Mapped[str | None] = mapped_column(String(128))
    # 险种清单，如 ["交强险","车辆损失险","第三者责任险","不计免赔"]
    coverage_types: Mapped[list] = mapped_column(JSONB, default=list)
    deductible: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # 绝对免赔额(元)
    payout_ratio: Mapped[float] = mapped_column(Numeric(4, 2), default=1.0)  # 赔付比例 0~1
    sum_insured: Mapped[float | None] = mapped_column(Numeric(12, 2))  # 车损保额(≈车辆价值)

    effective_from: Mapped[str | None] = mapped_column(String(32))
    effective_to: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)
